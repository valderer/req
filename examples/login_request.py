import getpass
import json
import os

import requests


LOGIN_URL = "https://b.kukahome.com/api/h5app/wxapp/login"
ADDRESS_URL = "https://b.kukahome.com/api/h5app/wxapp/member/address"
ADDRESS_LIST_URL = "https://b.kukahome.com/api/h5app/wxapp/member/addresslist"
TIMEOUT = 15
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
SENSITIVE_KEYWORDS = (
    "authorization",
    "cookie",
    "mobile",
    "password",
    "phone",
    "token",
    "username",
)


def mask_value(value):
    """隐藏 Token、手机号等敏感信息，避免被终端日志完整记录。"""
    text = str(value)
    if len(text) <= 8:
        return "***"
    return f"{text[:4]}...{text[-4:]}"


def sanitize(data):
    """递归处理响应，仅对常见敏感字段进行脱敏。"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            normalized_key = key.lower().replace("_", "").replace("-", "")
            is_sensitive = any(
                keyword in normalized_key for keyword in SENSITIVE_KEYWORDS
            )
            if is_sensitive and value is not None:
                result[key] = mask_value(value)
            else:
                result[key] = sanitize(value)
        return result

    if isinstance(data, list):
        return [sanitize(item) for item in data]

    return data


def load_env_file(file_path):
    """读取项目根目录的 .env，不覆盖系统中已经设置的环境变量。"""
    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def extract_authorization(response_data):
    """从登录响应中提取后续接口可直接使用的 Authorization 值。"""
    assert response_data.get("errcode") == 0, (
        f"登录失败：{response_data.get('errmsg', '未知错误')}"
    )

    authorization = response_data.get("token")
    if authorization:
        if authorization.lower().startswith("bearer "):
            return authorization
        return f"Bearer {authorization}"

    data = response_data.get("data") or {}
    raw_token = data.get("token")
    if not raw_token and isinstance(data.get("data"), dict):
        raw_token = data["data"].get("token")

    assert raw_token, "登录成功，但响应中没有找到 Token"
    return f"Bearer {raw_token}"


def add_address(authorization, company_id):
    """使用登录返回的 Token 添加一条收货地址。"""
    address_body = {
        "username": "lsf123",
        "telephone": "18288889999",
        "tmp_code": ["110000", "110100", "110102"],
        "adrdetail": "abcde",
        "province": "北京市",
        "city": "北京市",
        "county": "西城区",
        "is_def": 0,
        "company_id": company_id,
    }
    address_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": authorization,
    }

    print("\n========== 第二个请求：添加地址 ==========")
    print("请求方法：POST")
    print(f"请求地址：{ADDRESS_URL}")
    print("Authorization：已设置（完整 Token 不显示）")
    print("请求数据：")
    print(json.dumps(sanitize(address_body), ensure_ascii=False, indent=2))

    try:
        response = requests.post(
            ADDRESS_URL,
            json=address_body,
            headers=address_headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as error:
        print(f"添加地址请求失败：{error}")
        raise SystemExit(1) from error

    print(f"HTTP 状态码：{response.status_code}")
    print(f"响应类型：{response.headers.get('Content-Type')}")

    try:
        response_data = response.json()
    except requests.JSONDecodeError:
        print("服务器没有返回合法 JSON，原始响应如下：")
        print(response.text)
        raise SystemExit(1)

    print("脱敏后的响应 JSON：")
    print(json.dumps(sanitize(response_data), ensure_ascii=False, indent=2))

    assert response.status_code == 200, "添加地址接口 HTTP 状态码不是 200"
    return response_data


def query_addresses(authorization, company_id):
    """查询当前公司的地址列表。"""
    query_headers = {
        "Accept": "application/json",
        "Authorization": authorization,
    }
    query_params = {
        "company_id": company_id,
    }

    print("\n========== 第三个请求：查询地址列表 ==========")
    print("请求方法：GET")
    print(f"请求地址：{ADDRESS_LIST_URL}")
    print(f"查询参数：{query_params}")
    print("Authorization：已设置（完整 Token 不显示）")

    try:
        response = requests.get(
            ADDRESS_LIST_URL,
            params=query_params,
            headers=query_headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as error:
        print(f"查询地址请求失败：{error}")
        raise SystemExit(1) from error

    print(f"HTTP 状态码：{response.status_code}")
    print(f"响应类型：{response.headers.get('Content-Type')}")

    try:
        response_data = response.json()
    except requests.JSONDecodeError:
        print("服务器没有返回合法 JSON，原始响应如下：")
        print(response.text)
        raise SystemExit(1)

    print("脱敏后的响应 JSON：")
    print(json.dumps(sanitize(response_data), ensure_ascii=False, indent=2))

    assert response.status_code == 200, "查询地址接口 HTTP 状态码不是 200"
    return response_data


def delete_address(authorization, company_id, address_id):
    """删除本次流程刚刚创建的地址。"""
    delete_url = f"{ADDRESS_URL}/{address_id}"
    delete_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    delete_body = {
        "company_id": company_id,
    }

    print("\n========== 第四个请求：删除地址 ==========")
    print("请求方法：DELETE")
    print(f"请求地址：{delete_url}")
    print("Authorization：已设置（完整 Token 不显示）")
    print(f"请求数据：{delete_body}")

    try:
        response = requests.delete(
            delete_url,
            json=delete_body,
            headers=delete_headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as error:
        print(f"删除地址请求失败：{error}")
        raise SystemExit(1) from error

    print(f"HTTP 状态码：{response.status_code}")
    print(f"响应类型：{response.headers.get('Content-Type')}")

    try:
        response_data = response.json()
    except requests.JSONDecodeError:
        print("服务器没有返回合法 JSON，原始响应如下：")
        print(response.text)
        raise SystemExit(1)

    print("脱敏后的响应 JSON：")
    print(json.dumps(sanitize(response_data), ensure_ascii=False, indent=2))

    assert response.status_code == 200, "删除地址接口 HTTP 状态码不是 200"
    return response_data


def main():
    load_env_file(ENV_FILE)

    username = os.getenv("TEST_USERNAME") or input("请输入测试账号：").strip()
    password = os.getenv("TEST_PASSWORD") or getpass.getpass(
        "请输入接口要求的密码值（输入内容不会显示）："
    )
    company_id = os.getenv("TEST_COMPANY_ID", "2")

    request_body = {
        "username": username,
        "password": password,
        "company_id": company_id,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    print(f"请求方法：POST")
    print(f"请求地址：{LOGIN_URL}")
    print(
        "请求数据："
        + json.dumps(
            {
                "username": mask_value(username),
                "password": "***",
                "company_id": company_id,
            },
            ensure_ascii=False,
        )
    )

    try:
        response = requests.post(
            LOGIN_URL,
            json=request_body,
            headers=headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as error:
        print(f"请求失败：{error}")
        raise SystemExit(1) from error

    print(f"HTTP 状态码：{response.status_code}")
    print(f"响应类型：{response.headers.get('Content-Type')}")

    try:
        response_data = response.json()
    except requests.JSONDecodeError:
        print("服务器没有返回合法 JSON，原始响应如下：")
        print(response.text)
        raise SystemExit(1)

    print("脱敏后的响应 JSON：")
    print(json.dumps(sanitize(response_data), ensure_ascii=False, indent=2))

    assert response.status_code == 200, "登录接口 HTTP 状态码不是 200"
    authorization = extract_authorization(response_data)

    print("登录断言通过：errcode == 0")
    print("Token 提取成功：后续请求将使用 Authorization 请求头（完整值不显示）")
    print(f"认证类型：{authorization.split(' ', 1)[0]}")

    address_response_data = add_address(authorization, company_id)
    address_id = address_response_data.get("data", {}).get("address_id")
    assert address_id, "添加地址成功，但响应中没有找到 address_id"
    print(f"地址创建成功，address_id：{address_id}")

    try:
        query_addresses(authorization, company_id)
    finally:
        # 无论查询成功还是失败，都清理本次创建的测试地址。
        delete_address(authorization, company_id, address_id)


if __name__ == "__main__":
    main()
