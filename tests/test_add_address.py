from copy import deepcopy
from pathlib import Path

import allure
import pytest

from common.yaml_util import load_yaml


PROJECT_ROOT = Path(__file__).parents[1]
ADDRESS_TEST_DATA = load_yaml(PROJECT_ROOT / "data" / "address.yaml")
TELEPHONE_CASES = ADDRESS_TEST_DATA["telephone_cases"]


def extract_address_data(response_data):
    """安全地取得添加地址响应中的 data 对象。"""
    data = response_data.get("data")
    return data if isinstance(data, dict) else {}


@allure.feature("地址管理")
@allure.story("添加地址")
@pytest.mark.address
@pytest.mark.regression
class TestAddAddress:
    @pytest.mark.parametrize(
        "case",
        TELEPHONE_CASES,
        ids=[case["case_id"] for case in TELEPHONE_CASES],
    )
    def test_add_address_telephone(
        self,
        case,
        login_authorization,
        address_data,
        address_api,
    ):
        """使用等价类和边界值验证添加地址接口的手机号校验。"""
        allure.dynamic.title(case["title"])

        request_data = deepcopy(address_data)
        request_data["telephone"] = case["telephone"]

        response = address_api.add_address(
            authorization=login_authorization,
            address_data=request_data,
        )
        response_data = response.json()
        actual_address = extract_address_data(response_data)
        address_id = actual_address.get("address_id")

        allure.attach(
            str(response.status_code),
            name="HTTP 状态码",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            response.text,
            name="添加地址响应",
            attachment_type=allure.attachment_type.JSON,
        )

        try:
            if case["expected_valid"]:
                assert response.status_code == 200, (
                    f"合法手机号应返回 HTTP 200，实际为 {response.status_code}；"
                    f"响应：{response.text}"
                )
                assert address_id, (
                    f"合法手机号应成功创建地址并返回 address_id；响应：{response.text}"
                )
                assert actual_address["telephone"] == request_data["telephone"]
                assert actual_address["username"] == request_data["username"]
                assert actual_address["province"] == request_data["province"]
                assert actual_address["city"] == request_data["city"]
                assert actual_address["county"] == request_data["county"]
                assert actual_address["adrdetail"] == request_data["adrdetail"]
                assert int(actual_address["is_def"]) == int(request_data["is_def"])
            else:
                assert not address_id, (
                    f"无效手机号 {case['telephone']!r} 不应创建地址，"
                    f"但接口返回 address_id={address_id}"
                )
                assert response.status_code == case["expected_http_status"], (
                    "无效手机号的 HTTP 状态码不符合预期；"
                    f"预期={case['expected_http_status']}，"
                    f"实际={response.status_code}，响应：{response.text}"
                )
                error_data = response_data.get("error") or {}
                assert error_data.get("message") == case["expected_error_message"]
                assert error_data.get("status_code") == case["expected_error_status_code"]
        finally:
            # 即使无效手机号被接口错误地接受，也删除意外创建的数据。
            if address_id:
                delete_response = address_api.delete_address(
                    authorization=login_authorization,
                    company_id=request_data["company_id"],
                    address_id=address_id,
                )
                assert delete_response.status_code in (200, 204), (
                    f"测试数据清理失败，address_id={address_id}，"
                    f"HTTP 状态码={delete_response.status_code}"
                )
