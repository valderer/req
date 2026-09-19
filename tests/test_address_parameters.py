from copy import deepcopy
from pathlib import Path

import allure
import pytest

from common.yaml_util import load_yaml


PROJECT_ROOT = Path(__file__).parents[1]
ADDRESS_TEST_DATA = load_yaml(PROJECT_ROOT / "data" / "address.yaml")
TELEPHONE_CASES = ADDRESS_TEST_DATA["telephone_cases"]


def extract_address_data(response_data):
    data = response_data.get("data")
    return data if isinstance(data, dict) else {}


@allure.feature("地址管理")
@allure.story("添加地址参数校验")
@pytest.mark.address
@pytest.mark.regression
class TestAddressParameters:
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
        address_cleanup,
    ):
        """只验证添加地址接口的手机号参数，不执行查询和删除流程。"""
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

        if address_id:
            address_cleanup.append(
                {
                    "address_id": address_id,
                    "company_id": request_data["company_id"],
                }
            )

        allure.attach(
            response.text,
            name="添加地址响应",
            attachment_type=allure.attachment_type.JSON,
        )

        if case["expected_valid"]:
            assert response.status_code == 200, (
                f"合法手机号应返回 HTTP 200，实际为 {response.status_code}；"
                f"响应：{response.text}"
            )
            assert address_id, "合法手机号未返回 address_id"
            assert actual_address["telephone"] == request_data["telephone"]
            assert actual_address["username"] == request_data["username"]
            assert actual_address["province"] == request_data["province"]
            assert actual_address["city"] == request_data["city"]
            assert actual_address["county"] == request_data["county"]
            assert actual_address["adrdetail"] == request_data["adrdetail"]
            assert int(actual_address["is_def"]) == int(request_data["is_def"])
            return

        assert not address_id, (
            f"无效手机号 {case['telephone']!r} 不应创建地址，"
            f"但返回 address_id={address_id}"
        )
        assert response.status_code == case["expected_http_status"], (
            f"预期 HTTP {case['expected_http_status']}，"
            f"实际为 {response.status_code}；响应：{response.text}"
        )
        error_data = response_data.get("error") or {}
        assert error_data.get("message") == case["expected_error_message"]
        assert error_data.get("status_code") == case["expected_error_status_code"]
