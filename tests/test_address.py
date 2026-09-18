import allure
import pytest


def contains_value(data, expected):
    """递归判断查询响应中是否包含指定地址 ID。"""
    if isinstance(data, dict):
        return any(contains_value(value, expected) for value in data.values())
    if isinstance(data, list):
        return any(contains_value(item, expected) for item in data)
    return str(data) == str(expected)


@allure.feature("地址管理")
@allure.story("地址全流程")
@pytest.mark.address
@pytest.mark.smoke
class TestAddress:
    @allure.title("登录、添加、查询、删除地址")
    def test_address_flow(self, login_authorization, address_data, address_api):
        add_response = address_api.add_address(
            authorization=login_authorization,
            address_data=address_data,
        )

        assert add_response.status_code == 200, (
            f"添加地址失败：HTTP {add_response.status_code}，响应：{add_response.text}"
        )
        add_response_data = add_response.json()
        assert add_response_data.get("errcode", 0) == 0
        address_id = add_response_data["data"]["address_id"]
        assert address_id
        added_address = add_response_data["data"]
        assert str(added_address["company_id"]) == str(address_data["company_id"])
        assert added_address["telephone"] == address_data["telephone"]
        assert added_address["province"] == address_data["province"]
        assert added_address["city"] == address_data["city"]
        assert added_address["county"] == address_data["county"]

        try:
            query_response = address_api.query_addresses(
                authorization=login_authorization,
                company_id=address_data["company_id"],
            )

            assert query_response.status_code == 200, (
                f"查询地址失败：HTTP {query_response.status_code}，"
                f"响应：{query_response.text}"
            )
            query_response_data = query_response.json()
            assert contains_value(query_response_data, address_id)
        finally:
            delete_response = address_api.delete_address(
                authorization=login_authorization,
                company_id=address_data["company_id"],
                address_id=address_id,
            )

            assert delete_response.status_code in (200, 204)
            if delete_response.status_code == 200:
                assert delete_response.json().get("data", {}).get("status") is True
