import urllib3
import ssl
import socket

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HTTPClient:
    """HTTP 客户端，负责发送 HTTP 请求"""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.http = urllib3.PoolManager()
    
    def _send_raw(self, method, url, headers, body, http_version):
        """使用原始 socket 发送请求，支持自定义 HTTP 版本"""
        # 解析 URL
        parsed = urllib3.util.url.parse_url(url)
        host = parsed.host
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        path = parsed.path or '/'
        if parsed.query:
            path += '?' + parsed.query

        # 构建请求行
        request_line = f"{method} {path} HTTP/{http_version}\r\n"

        # 构建请求头
        header_lines = []
        for key, value in headers.items():
            header_lines.append(f"{key}: {value}")
        if body:
            header_lines.append(f"Content-Length: {len(body)}")
        header_block = "\r\n".join(header_lines) + "\r\n"

        # 组合完整请求（body 已在入口归一化为 bytes，直接按二进制流拼接，不做类型判断）
        request = request_line + header_block + "\r\n"
        request = request.encode('utf-8') + (body if body else b'')

        # 建立连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            if parsed.scheme == 'https':
                context = ssl._create_unverified_context()
                sock = context.wrap_socket(sock, server_hostname=host)
                sock.connect((host, port))
            else:
                sock.connect((host, port))
            sock.sendall(request)

            # 接收响应
            response_data = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                # 简单判断响应是否完整（读到空行结束）
                if b"\r\n\r\n" in response_data:
                    # 对于有 body 的响应，尝试读到 close
                    break
        finally:
            sock.close()

        # 解析响应
        try:
            response_text = response_data.decode('utf-8', errors='ignore')
            return self._parse_response(response_text, url)
        except Exception as e:
            return self._make_error_response(f"响应解析失败: {e}", url)

    def _parse_response(self, response_text, url):
        """解析原始 HTTP 响应"""
        parts = response_text.split('\r\n\r\n', 1)
        status_line_and_headers = parts[0]
        body = parts[1] if len(parts) > 1 else ""

        lines = status_line_and_headers.split('\r\n')
        status_line = lines[0]

        # 解析状态码
        match = status_line.split(' ', 2)
        status_code = int(match[1]) if len(match) >= 2 else 0

        # 解析响应头
        response_headers = {}
        for line in lines[1:]:
            if ': ' in line:
                key, value = line.split(': ', 1)
                response_headers[key] = value

        class RawResponse:
            def __init__(self, status_code, headers, text, url):
                self.status_code = status_code
                self.headers = headers
                self.text = text
                self.url = url

        return RawResponse(status_code, response_headers, body, url)

    def _make_error_response(self, error_text, url):
        """生成错误响应对象"""
        class ErrorResponse:
            def __init__(self, error, url):
                self.status_code = 0
                self.headers = {}
                self.text = f"请求失败: {str(error)}"
                self.url = url
        return ErrorResponse(error_text, url)

    def send_request(self, method, url, headers, body, http_version='1.1', redirect=False, retries=False):
        """发送 HTTP 请求，支持多个重名 header，body 统一按二进制流发送"""
        # 统一将 body 归一化为 bytes（str 编码为 utf-8，bytes/None 原样处理），直接按二进制流发送
        if body is None:
            body = b''
        elif isinstance(body, str):
            body = body.encode('utf-8')

        # 如果 HTTP 版本不是标准 1.1，走 raw socket 路径
        if http_version != '1.1':
            return self._send_raw(method, url, headers, body, http_version)

        try:
            response = self.http.request(
                method=method,
                url=url,
                headers=headers,
                body=body,
                redirect=redirect,
                retries=retries,
                timeout=self.timeout
            )

            # 包装响应对象
            class Urllib3Response:
                def __init__(self, urllib3_response, url):
                    self.status_code = urllib3_response.status
                    self.headers = urllib3_response.getheaders()
                    self.text = urllib3_response.data.decode('utf-8', errors='ignore')
                    self.url = url

            return Urllib3Response(response, url)
        except Exception as e:
            return self._make_error_response(e, url)