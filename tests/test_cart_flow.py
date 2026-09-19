import allure
import pytest

from tests.cart_helpers import find_cart


@allure.feature("购物车")
@allure.story("购物车业务流程")
@pytest.mark.cart
@pytest.mark.regression
class TestCartFlow:
    @allure.title("添加、查询、删除并确认购物车商品不存在")
    @pytest.mark.smoke
    def test_cart_flow(
        self,
        login_authorization,
        cart_api,
        cart_data,
        cart_cleanup,
    ):
        with allure.step("添加商品到购物车"):
            add_response = cart_api.add_to_cart(
                authorization=login_authorization,
                cart_data=cart_data,
            )

        assert add_response.status_code in (200, 201)
        cart = add_response.json().get("data") or {}
        cart_id = cart.get("cart_id")
        assert cart_id, "添加购物车成功，但没有返回 cart_id"

        cleanup_record = {
            "cart_id": cart_id,
            "company_id": cart_data["company_id"],
        }
        cart_cleanup.append(cleanup_record)

        assert str(cart["item_id"]) == str(cart_data["item_id"])
        assert cart["num"] == cart_data["num"]
        assert cart["cart_type"] == cart_data["cart_type"]

        with allure.step("查询并确认商品存在"):
            list_response = cart_api.list_cart(
                authorization=login_authorization,
                shop_type=cart_data["shop_type"],
                company_id=cart_data["company_id"],
            )

        assert list_response.status_code == 200
        queried_cart = find_cart(
            list_response.json()["data"],
            cart_id,
            section="valid_cart",
        )
        assert queried_cart is not None, f"没有找到 cart_id={cart_id}"
        assert queried_cart["num"] == cart_data["num"]
        assert queried_cart["total_fee"] == (
            queried_cart["price"] * queried_cart["num"]
        )

        with allure.step("删除购物车商品"):
            delete_response = cart_api.delete_cart(
                authorization=login_authorization,
                cart_id=cart_id,
                company_id=cart_data["company_id"],
            )

        assert delete_response.status_code == 200
        assert delete_response.json().get("data", {}).get("status") is True

        with allure.step("删除后查询并确认商品不存在"):
            after_delete_response = cart_api.list_cart(
                authorization=login_authorization,
                shop_type=cart_data["shop_type"],
                company_id=cart_data["company_id"],
            )

        assert after_delete_response.status_code == 200
        assert find_cart(after_delete_response.json()["data"], cart_id) is None, (
            f"商品删除后仍能查询到 cart_id={cart_id}"
        )
        cart_cleanup.remove(cleanup_record)
