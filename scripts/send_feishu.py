"""发送 Jenkins 构建结果到飞书群机器人。"""

import json
import os
import urllib.request
import xml.etree.ElementTree as ET


status = os.environ.get("FEISHU_STATUS", "failure")
status_text = "成功" if status == "success" else "失败"


def read_test_statistics():
    """读取 pytest 生成的 JUnit XML，失败时返回空统计。"""
    result = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "duration": "-",
    }
    report_path = "reports/junit.xml"
    if not os.path.exists(report_path):
        return result

    try:
        root = ET.parse(report_path).getroot()
        suites = [root] if root.tag == "testsuite" else root.findall(".//testsuite")
        result["total"] = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
        result["failed"] = sum(
            int(suite.attrib.get("failures", 0)) for suite in suites
        )
        result["errors"] = sum(
            int(suite.attrib.get("errors", 0)) for suite in suites
        )
        result["skipped"] = sum(
            int(suite.attrib.get("skipped", 0)) for suite in suites
        )
        result["passed"] = max(
            result["total"]
            - result["failed"]
            - result["errors"]
            - result["skipped"],
            0,
        )
        total_time = sum(float(suite.attrib.get("time", 0)) for suite in suites)
        result["duration"] = f"{total_time:.2f}s"
    except (ET.ParseError, ValueError, TypeError):
        pass
    return result


stats = read_test_statistics()
branch = os.environ.get("GIT_BRANCH", "main").replace("origin/", "")
commit = os.environ.get("GIT_COMMIT", "")[:8] or "未知"
build_url = os.environ.get("BUILD_URL", "")
allure_url = f"{build_url}allure/" if build_url else ""
message = "\n".join(
    [
        f"Jenkins 自动化测试{status_text}",
        f"项目：{os.environ.get('JOB_NAME', '')}",
        f"构建：#{os.environ.get('BUILD_NUMBER', '')}",
        f"分支：{branch}",
        f"提交：{commit}",
        "",
        (
            "测试统计："
            f"总计 {stats['total']}，通过 {stats['passed']}，"
            f"失败 {stats['failed']}，跳过 {stats['skipped']}，"
            f"错误 {stats['errors']}"
        ),
        f"测试耗时：{stats['duration']}",
        f"Jenkins：{build_url}",
        f"Allure：{allure_url}",
    ]
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
