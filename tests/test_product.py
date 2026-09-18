import json
from copy import deepcopy
from pathlib import Path

import allure
import pytest

from common.yaml_util import load_yaml


PROJECT_ROOT = Path(__file__).parents[1]
PRODUCT_DATA = load_yaml(PROJECT_ROOT / "data" / "product.yaml")


@allure.feature("商品管理")
@allure.story("商品列表")
@pytest.mark.product
@pytest.mark.regression
class TestProduct:
    @allure.title("商品列表查询成功")
    @pytest.mark.smoke
    def test_list_products(self, product_api):
        query_params = PRODUCT_DATA["list_products"]
        response = product_api.list_products(query_params)

        allure.attach(
            json.dumps(query_params, ensure_ascii=False, indent=2),
            name="查询参数",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            response.text,
            name="商品列表响应",
            attachment_type=allure.attachment_type.JSON,
        )

        assert response.status_code == 200, (
            f"查询商品失败：HTTP {response.status_code}，响应：{response.text}"
        )

        response_data = response.json()
        data = response_data.get("data")
        assert isinstance(data, dict), "响应 data 必须是对象"
        assert isinstance(data.get("total_count"), int), (
            "响应 data.total_count 必须是整数"
        )
        assert isinstance(data.get("list"), list), "响应 data.list 必须是列表"

        for item in data["list"]:
            assert item.get("item_id"), "商品必须返回 item_id"
            assert item.get("item_name"), "商品必须返回 item_name"
            assert item.get("company_id") == query_params["company_id"]

    @allure.title("商品列表分页查询")
    @pytest.mark.parametrize(
        "case",
        PRODUCT_DATA["page_cases"],
        ids=[case["case_id"] for case in PRODUCT_DATA["page_cases"]],
    )
    def test_list_products_by_page(self, product_api, case):
        query_params = deepcopy(PRODUCT_DATA["list_products"])
        query_params.update(
            page=case["page"],
            pageSize=case["pageSize"],
        )

        response = product_api.list_products(query_params)

        assert response.status_code == 200, (
            f"分页查询商品失败：HTTP {response.status_code}，响应：{response.text}"
        )
        data = response.json().get("data") or {}
        products = data.get("list")
        assert isinstance(products, list), "分页响应 data.list 必须是列表"
        assert len(products) <= case["pageSize"], (
            f"返回商品数量超过 pageSize：数量={len(products)}，"
            f"pageSize={case['pageSize']}"
        )
