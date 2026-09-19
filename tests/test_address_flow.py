import allure
import pytest


def contains_value(data, expected):
    """递归判断响应中是否包含指定值。"""
    if isinstance(data, dict):
        return any(contains_value(value, expected) for value in data.values())
    if isinstance(data, list):
        return any(contains_value(item, expected) for item in data)
    return str(data) == str(expected)


@allure.feature("地址管理")
@allure.story("地址业务流程")
@pytest.mark.address
@pytest.mark.smoke
@pytest.mark.regression
class TestAddressFlow:
    @allure.title("添加、查询、删除并确认地址不存在")
    def test_address_flow(
        self,
        login_authorization,
        address_data,
        address_api,
        address_cleanup,
    ):
        with allure.step("添加地址"):
            add_response = address_api.add_address(
                authorization=login_authorization,
                address_data=address_data,
            )

        assert add_response.status_code == 200, (
            f"添加地址失败：HTTP {add_response.status_code}，"
            f"响应：{add_response.text}"
        )
        added_address = add_response.json()["data"]
        address_id = added_address.get("address_id")
        assert address_id, "添加地址成功，但没有返回 address_id"

        cleanup_record = {
            "address_id": address_id,
            "company_id": address_data["company_id"],
        }
        address_cleanup.append(cleanup_record)

        assert str(added_address["company_id"]) == str(address_data["company_id"])
        assert added_address["telephone"] == address_data["telephone"]
        assert added_address["province"] == address_data["province"]
        assert added_address["city"] == address_data["city"]
        assert added_address["county"] == address_data["county"]

        with allure.step("查询并确认地址存在"):
            query_response = address_api.query_addresses(
                authorization=login_authorization,
                company_id=address_data["company_id"],
            )

        assert query_response.status_code == 200
        assert contains_value(query_response.json(), address_id), (
            f"查询结果中没有找到 address_id={address_id}"
        )

        with allure.step("删除地址"):
            delete_response = address_api.delete_address(
                authorization=login_authorization,
                company_id=address_data["company_id"],
                address_id=address_id,
            )

        assert delete_response.status_code in (200, 204)
        if delete_response.status_code == 200:
            assert delete_response.json().get("data", {}).get("status") is True

        with allure.step("删除后查询并确认地址不存在"):
            after_delete_response = address_api.query_addresses(
                authorization=login_authorization,
                company_id=address_data["company_id"],
            )

        assert after_delete_response.status_code == 200
        assert not contains_value(after_delete_response.json(), address_id), (
            f"地址删除后仍能查询到 address_id={address_id}"
        )
        address_cleanup.remove(cleanup_record)
