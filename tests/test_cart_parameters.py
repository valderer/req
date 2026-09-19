import json
from pathlib import Path

import allure
import pytest

from common.yaml_util import load_yaml


PROJECT_ROOT = Path(__file__).parents[1]
CART_TEST_DATA = load_yaml(PROJECT_ROOT / "data" / "cart.yaml")
QUANTITY_CASES = CART_TEST_DATA["quantity_cases"]


@allure.feature("购物车")
@allure.story("添加购物车参数校验")
@pytest.mark.cart
@pytest.mark.regression
class TestCartParameters:
    @pytest.mark.parametrize(
        "case",
        QUANTITY_CASES,
        ids=[case["case_id"] for case in QUANTITY_CASES],
    )
    def test_add_cart_quantity(
        self,
        login_authorization,
        cart_api,
        cart_data,
        cart_cleanup,
        case,
    ):
        """只验证添加购物车接口的数量参数，不执行完整业务流程。"""
        allure.dynamic.title(case["title"])
        request_data = cart_data.copy()
        request_data["num"] = case["num"]

        response = cart_api.add_to_cart(
            authorization=login_authorization,
            cart_data=request_data,
        )
        response_data = response.json()
        cart = response_data.get("data") or {}
        cart_id = cart.get("cart_id")

        if cart_id:
            cart_cleanup.append(
                {"cart_id": cart_id, "company_id": request_data["company_id"]}
            )

        allure.attach(
            json.dumps(request_data, ensure_ascii=False, indent=2),
            name="请求参数",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            response.text,
            name="添加购物车响应",
            attachment_type=allure.attachment_type.JSON,
        )

        if case["expected_valid"]:
            assert response.status_code in (200, 201)
            assert cart_id, "合法数量未返回 cart_id"
            assert str(cart["company_id"]) == str(request_data["company_id"])
            assert str(cart["item_id"]) == str(request_data["item_id"])
            assert cart["num"] == request_data["num"]
            assert cart["cart_type"] == request_data["cart_type"]
            return

        assert not cart_id, (
            f"数量 {case['num']} 不应创建购物车记录，"
            f"但返回 cart_id={cart_id}"
        )
        assert 400 <= response.status_code < 500 or response_data.get("error"), (
            f"非法数量应返回 4xx 或错误信息，响应：{response.text}"
        )
