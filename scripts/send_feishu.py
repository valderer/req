"""发送 Jenkins 构建结果到飞书群机器人。"""

import json
import os
import urllib.request


status = os.environ.get("FEISHU_STATUS", "failure")
status_text = "成功" if status == "success" else "失败"
message = (
    f"Jenkins 自动化测试{status_text}\n"
    f"项目：{os.environ.get('JOB_NAME', '')}\n"
    f"构建：#{os.environ.get('BUILD_NUMBER', '')}\n"
    f"详情：{os.environ.get('BUILD_URL', '')}"
)
payload = json.dumps(
    {
        "msg_type": "text",
        "content": {"text": message},
    },
    ensure_ascii=False,
).encode("utf-8")
request = urllib.request.Request(
    os.environ["FEISHU_WEBHOOK"],
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(request, timeout=10) as response:
        print(f"飞书通知已发送，HTTP {response.status}")
except Exception as error:
    # 通知失败不应覆盖真正的测试结果。
    print(f"飞书通知发送失败：{type(error).__name__}")
