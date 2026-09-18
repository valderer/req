import json

import requests


# 这是一个真实的公开 HTTP 接口，不需要账号和 Token。
url = "https://jsonplaceholder.typicode.com/posts/1"

print("1. 准备发送 GET 请求")
print(f"请求地址：{url}")

response = requests.get(url, timeout=10)

print("\n2. 收到服务器响应")
print(f"实际请求地址：{response.request.url}")
print(f"请求方法：{response.request.method}")
print(f"状态码：{response.status_code}")
print(f"响应类型：{response.headers.get('Content-Type')}")

print("\n3. 响应 JSON")
print(json.dumps(response.json(), ensure_ascii=False, indent=2))

print("\n4. 验证结果")
assert response.status_code == 200
assert response.json()["id"] == 1
print("测试通过：状态码是 200，并且文章 id 是 1")

print(response.text())