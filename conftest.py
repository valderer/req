import os
from pathlib import Path

import pytest

from api.address_api import AddressApi
from api.cart_api import CartApi
from api.login_api import LoginApi
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
def cart_api(site_client):
    return CartApi(site_client)
