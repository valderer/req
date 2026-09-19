import os
from pathlib import Path

import pytest

from api.address_api import AddressApi
from api.cart_api import CartApi
from api.login_api import LoginApi
from api.product_api import ProductApi
from common.env_util import load_env_file
from common.request_client import RequestClient
from common.yaml_util import load_yaml


PROJECT_ROOT = Path(__file__).parent
load_env_file(PROJECT_ROOT / ".env")


@pytest.fixture(scope="session")
def client():
    config = load_yaml(PROJECT_ROOT / "config" / "config.yaml")
    return RequestClient(
        base_url=config["base_url"],
        timeout=config.get("timeout", 10),
    )

@pytest.fixture(scope="session")
def site_client():
    return RequestClient(
        base_url=os.environ["BASE_URL"],
        timeout=int(os.environ.get("TEST_TIMEOUT", "15")),
    )


@pytest.fixture(scope="session")
def login_authorization(site_client):
    response = LoginApi(site_client).login(
        username=os.environ["TEST_USERNAME"],
        password=os.environ["TEST_PASSWORD"],
        company_id=os.environ.get("TEST_COMPANY_ID", "2"),
    )

    assert response.status_code == 200
    return LoginApi.extract_authorization(response.json())


@pytest.fixture
def address_api(site_client):
    return AddressApi(site_client)


@pytest.fixture
def address_data():
    return load_yaml(PROJECT_ROOT / "data" / "address.yaml")["normal_address"]


@pytest.fixture
def address_cleanup(login_authorization, address_api):
    """记录测试创建的地址，并在测试结束后统一清理。"""
    created_addresses = []
    yield created_addresses

    for address in reversed(created_addresses):
        response = address_api.delete_address(
            authorization=login_authorization,
            company_id=address["company_id"],
            address_id=address["address_id"],
        )
        assert response.status_code in (200, 204), (
            f"地址清理失败：address_id={address['address_id']}，"
            f"HTTP {response.status_code}，响应：{response.text}"
        )


@pytest.fixture
def cart_api(site_client):
    return CartApi(site_client)


@pytest.fixture
def cart_data():
    return load_yaml(PROJECT_ROOT / "data" / "cart.yaml")["add_cart"]


@pytest.fixture
def cart_cleanup(login_authorization, cart_api):
    """记录测试创建的购物车数据，并在测试结束后统一清理。"""
    created_carts = []
    yield created_carts

    for cart in reversed(created_carts):
        response = cart_api.delete_cart(
            authorization=login_authorization,
            cart_id=cart["cart_id"],
            company_id=cart["company_id"],
        )
        assert response.status_code == 200, (
            f"购物车清理失败：cart_id={cart['cart_id']}，"
            f"HTTP {response.status_code}，响应：{response.text}"
        )
        assert response.json().get("data", {}).get("status") is True


@pytest.fixture
def product_api(site_client):
    return ProductApi(site_client)
