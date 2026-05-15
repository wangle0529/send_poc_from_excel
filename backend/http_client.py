import urllib3
from urllib3._collections import HTTPHeaderDict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HTTPClient:
    """HTTP 客户端，负责发送 HTTP 请求"""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.http = urllib3.PoolManager()
    
    def send_request(self, method, url, headers, body, redirect=False, retries=False):
        """发送 HTTP 请求，支持多个重名 header"""
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
            # 发生异常时返回错误对象
            class ErrorResponse:
                def __init__(self, error, url):
                    self.status_code = 0
                    self.headers = {}
                    self.text = f"请求失败: {str(e)}"
                    self.url = url
            
            return ErrorResponse(e, url)