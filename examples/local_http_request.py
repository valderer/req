import json

import requests


url = "http://127.0.0.1:8000/posts/1"

print("1. 准备发送请求")
print(f"请求方法：GET")
print(f"请求地址：{url}")

response = requests.get(url, timeout=5)

print("\n2. 收到响应")
print(f"状态码：{response.status_code}")
print(f"响应类型：{response.headers.get('Content-Type')}")
print(f"原始响应文本：{response.text}")

print("\n3. 响应 JSON")
print(json.dumps(response.json(), ensure_ascii=False, indent=2))

print("\n4. 执行断言")
assert response.status_code == 200
assert response.json()["id"] == 1
assert response.json()["title"] == "我的第一篇文章"
print("测试通过：服务器返回了预期的状态码和文章数据")
