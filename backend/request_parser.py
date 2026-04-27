import re
from urllib3._collections import HTTPHeaderDict

class RequestParser:
    """请求报文解析器"""
    
    def parse(self, raw_request):
        """解析 HTTP 请求报文"""
        # 解码和预处理
        decoded_request = raw_request
        decoded_request = decoded_request.replace('_x000D_', '')
        decoded_request = decoded_request.replace('\u200b', '')
        
        # 分割头部和 body
        if '\r\n\r\n' in decoded_request:
            header_body_split = decoded_request.split('\r\n\r\n')
        else:
            header_body_split = decoded_request.split('\n\n')
        
        headers_str = header_body_split[0]
        # 处理 accept-encoding
        headers_str = re.sub(r'accept-encoding:\s*.*', 'accept-encoding: gzip, deflate', headers_str, flags=re.IGNORECASE)
        
        # 构建 body
        body_str = ""
        for i in range(len(header_body_split)):
            if i == 1:
                body_str += header_body_split[i]
            if i > 1:
                body_str += "\n\n" + header_body_split[i]
        body_str = body_str.replace('\n', '\r\n')
        
        # 解析请求行
        request_line = headers_str.splitlines()[0].strip()
        match = re.match(r'^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH|TRACE|CONNECT)\s+([^\s]+)\s+HTTP/([\d.]+)$', request_line)
        
        if not match:
            raise ValueError("无效的请求行")
        
        method, path, http_version = match.groups()
        
        # 解析请求头
        headers = HTTPHeaderDict()
        for line in headers_str.splitlines()[1:]:
            line = line.strip()
            if not line:
                continue
            if re.match(r'^[^:]+:$', line):
                key, value = line.split(':', 1)
                headers.add(key, value.strip())
            elif ': ' in line:
                key, value = line.split(': ', 1)
                headers.add(key, value)
            elif ':' in line:
                key, value = line.split(':', 1)
                headers.add(key, value.strip())
        
        # 处理 Content-Length
        real_content_length = len(body_str)
        if real_content_length == 0:
            keys_to_delete = [key for key in headers if key.lower() == 'content-length']
            for key in keys_to_delete:
                del headers[key]
        
        # 自动添加 User-Agent
        has_user_agent = any(key.lower() == 'user-agent' for key in headers)
        if not has_user_agent:
            headers.add('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        return {
            'method': method,
            'path': path,
            'http_version': http_version,
            'headers': headers,
            'body': body_str,
            'content_length': real_content_length
        }