class ProductApi:
    """商品查询接口封装。"""

    ITEMS_PATH = "/api/h5app/wxapp/goods/items"

    def __init__(self, client):
        self.client = client

    def list_products(self, query_params):
        return self.client.get(
            self.ITEMS_PATH,
            params=query_params,
            headers={"Accept": "application/json"},
        )
