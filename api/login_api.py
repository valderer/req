class LoginApi:
    """登录接口封装。只负责发送登录请求和提取认证信息。"""

    PATH = "/api/h5app/wxapp/login"

    def __init__(self, client):
        self.client = client

    def login(self, username, password, company_id):
        # 避免 Pytest 在异常堆栈中展示本函数参数里的账号和密码。
        __tracebackhide__ = True
        return self.client.post(
            self.PATH,
            json={
                "username": username,
                "password": password,
                "company_id": company_id,
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    @staticmethod
    def extract_authorization(response_data):
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
