import json
from pathlib import Path

import allure
import pytest

from api.cart_api import CartApi
from common.yaml_util import load_yaml


PROJECT_ROOT = Path(__file__).parents[1]
TEST_DATA = load_yaml(PROJECT_ROOT / "data" / "cart.yaml")
QUANTITY_CASES = TEST_DATA["quantity_cases"]


def extract_cart_items(cart_data, section):
    """兼容 valid_cart 分组结构和 invalid_cart 直接列表结构。"""
    cart_items = cart_data.get(section, [])

    if section == "invalid_cart":
        return cart_items

    return [
        item
        for group in cart_items
        for item in group.get("list", [])
    ]


@allure.feature("购物车")
@allure.story("添加购物车")
@pytest.mark.cart
@pytest.mark.regression
class TestCart:
    @allure.title("商品添加购物车成功")
    @pytest.mark.parametrize(
        "case",
        QUANTITY_CASES,
        ids=[case["case_id"] for case in QUANTITY_CASES],
    )
    def test_add_to_cart(self, login_authorization, cart_api, case):
        allure.dynamic.title(case["title"])
        cart_data = TEST_DATA["add_cart"].copy()
        cart_data["num"] = case["num"]
        with allure.step("添加商品到购物车"):
            response = cart_api.add_to_cart(
                authorization=login_authorization,
                cart_data=cart_data,
            )

        allure.attach(
            json.dumps(cart_data, ensure_ascii=False, indent=2),
            name="请求参数",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            response.text,
            name="响应内容",
            attachment_type=allure.attachment_type.JSON,
        )

        response_data = response.json()
        cart = response_data.get("data") or {}
        cart_id = cart.get("cart_id")

        if not case["expected_valid"]:
            try:
                assert not cart_id, (
                    f"数量 {case['num']} 不应创建购物车记录，"
                    f"但返回 cart_id={cart_id}"
                )
                assert 400 <= response.status_code < 500 or response_data.get("error"), (
                    f"非法数量应返回 4xx 或错误信息，响应：{response.text}"
                )
            finally:
                if cart_id:
                    delete_response = cart_api.delete_cart(
                        authorization=login_authorization,
                        cart_id=cart_id,
                        company_id=cart_data["company_id"],
                    )
                    assert delete_response.status_code == 200
            return

        assert cart_id, "添加购物车成功，但没有返回 cart_id"
        assert str(cart["company_id"]) == str(cart_data["company_id"])
        assert str(cart["item_id"]) == str(cart_data["item_id"])
        assert cart["num"] == cart_data["num"]
        assert cart["cart_type"] == cart_data["cart_type"]

        try:
            with allure.step("查询购物车"):
                list_response = cart_api.list_cart(
                    authorization=login_authorization,
                    shop_type=cart_data["shop_type"],
                    company_id=cart_data["company_id"],
                )

            assert list_response.status_code == 200, (
                f"查询购物车失败：HTTP {list_response.status_code}，"
                f"响应：{list_response.text}"
            )

            list_data = list_response.json()["data"]
            expected_section = case.get("expected_cart_section", "valid_cart")
            cart_items = extract_cart_items(list_data, expected_section)
            queried_cart = next(
                (
                item
                for item in cart_items
                if str(item.get("cart_id")) == str(cart_id)
                ),
                None,
            )

            assert queried_cart is not None, (
                f"查询结果中没有找到刚添加的 cart_id={cart_id}"
            )
            assert str(queried_cart["item_id"]) == str(cart_data["item_id"])
            assert queried_cart["num"] == cart_data["num"]
            assert queried_cart["shop_type"] == cart_data["shop_type"]
            if expected_section == "valid_cart":
                assert queried_cart["total_fee"] == (
                    queried_cart["price"] * queried_cart["num"]
                )
        finally:
            with allure.step("删除购物车商品"):
                delete_response = cart_api.delete_cart(
                    authorization=login_authorization,
                    cart_id=cart_id,
                    company_id=cart_data["company_id"],
                )

            assert delete_response.status_code == 200
            assert delete_response.json()["data"]["status"] is True

            with allure.step("删除后再次查询购物车"):
                after_delete_response = cart_api.list_cart(
                    authorization=login_authorization,
                    shop_type=cart_data["shop_type"],
                    company_id=cart_data["company_id"],
                )

            assert after_delete_response.status_code == 200
            after_delete_data = after_delete_response.json()["data"]
            after_delete_items = (
                extract_cart_items(after_delete_data, "valid_cart")
                + extract_cart_items(after_delete_data, "invalid_cart")
            )

            assert not any(
                str(item.get("cart_id")) == str(cart_id)
                for item in after_delete_items
            ), f"删除后仍能查询到 cart_id={cart_id}"

    @pytest.mark.manual
    @allure.title("手动验证数量为 0 时保留购物车记录")
    def test_add_to_cart_quantity_zero_keep_record(
        self,
        login_authorization,
        cart_api,
    ):
        """故意不删除数据，仅用于观察数量为 0 的接口实际行为。"""
        cart_data = TEST_DATA["add_cart"].copy()
        cart_data["num"] = 0

        response = cart_api.add_to_cart(
            authorization=login_authorization,
            cart_data=cart_data,
        )

        assert response.status_code in (200, 201)
        cart_id = response.json()["data"]["cart_id"]
        assert cart_id

        print(f"数量为 0 的购物车记录已保留，cart_id={cart_id}")
