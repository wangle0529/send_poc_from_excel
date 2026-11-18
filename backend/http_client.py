import time
import urllib3
import ssl
import socket

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HTTPClient:
    """HTTP 客户端，负责发送 HTTP 请求"""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        # 创建不验证证书的 SSL 上下文（内网测试环境常为自签名证书，忽略证书校验）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        self.http = urllib3.PoolManager(ssl_context=ssl_context)
    
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
        has_content_length = False
        for key, value in headers.items():
            header_lines.append(f"{key}: {value}")
            if key.lower() == 'content-length':
                has_content_length = True
        # 仅当请求头中没有 Content-Length 时才补充，避免重复
        if body and not has_content_length:
            header_lines.append(f"Content-Length: {len(body)}")
        header_block = "\r\n".join(header_lines) + "\r\n"

        # 组合完整请求（body 已在入口归一化为 bytes，直接按二进制流拼接，不做类型判断）
        request = request_line + header_block + "\r\n"
        request = request.encode('utf-8') + (body if body else b'')

        # 建立连接（开始计时）
        start = time.perf_counter()
        ttfb_ms = None
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
                if ttfb_ms is None:
                    ttfb_ms = (time.perf_counter() - start) * 1000
                response_data += chunk
                # 简单判断响应是否完整（读到空行结束）
                if b"\r\n\r\n" in response_data:
                    # 对于有 body 的响应，尝试读到 close
                    break
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            sock.close()

        # 解析响应
        try:
            response_text = response_data.decode('utf-8', errors='ignore')
            return self._parse_response(response_text, url, elapsed_ms, ttfb_ms)
        except Exception as e:
            return self._make_error_response(f"响应解析失败: {e}", url, elapsed_ms, ttfb_ms)

    def _parse_response(self, response_text, url, elapsed_ms=None, ttfb_ms=None):
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
            def __init__(self, status_code, headers, text, url, elapsed_ms=None, ttfb_ms=None):
                self.status_code = status_code
                self.headers = headers
                self.text = text
                self.url = url
                self.elapsed_ms = elapsed_ms
                self.ttfb_ms = ttfb_ms if ttfb_ms is not None else elapsed_ms

        return RawResponse(status_code, response_headers, body, url, elapsed_ms, ttfb_ms)

    def _make_error_response(self, error_text, url, elapsed_ms=None, ttfb_ms=None):
        """生成错误响应对象"""
        class ErrorResponse:
            def __init__(self, error, url, elapsed_ms=None, ttfb_ms=None):
                self.status_code = 0
                self.headers = {}
                self.text = f"请求失败: {str(error)}"
                self.url = url
                self.elapsed_ms = elapsed_ms
                self.ttfb_ms = ttfb_ms if ttfb_ms is not None else elapsed_ms
        return ErrorResponse(error_text, url, elapsed_ms, ttfb_ms)

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

        start = time.perf_counter()
        try:
            # preload_content=False：响应头到达后立即返回，便于区分首字节耗时与总耗时
            response = self.http.request(
                method=method,
                url=url,
                headers=headers,
                body=body,
                redirect=redirect,
                retries=retries,
                timeout=self.timeout,
                preload_content=False
            )
            ttfb_ms = (time.perf_counter() - start) * 1000
            data = response.read()
            elapsed_ms = (time.perf_counter() - start) * 1000
            status_code = response.status
            resp_headers = response.getheaders()
            response.release_conn()

            # 包装响应对象
            class Urllib3Response:
                def __init__(self, status_code, headers, text, url, elapsed_ms=None, ttfb_ms=None):
                    self.status_code = status_code
                    self.headers = headers
                    self.text = text
                    self.url = url
                    self.elapsed_ms = elapsed_ms
                    self.ttfb_ms = ttfb_ms if ttfb_ms is not None else elapsed_ms

            return Urllib3Response(
                status_code,
                resp_headers,
                data.decode('utf-8', errors='ignore'),
                url,
                elapsed_ms,
                ttfb_ms
            )
        except Exception as e:
            return self._make_error_response(e, url, (time.perf_counter() - start) * 1000)