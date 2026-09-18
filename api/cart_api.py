class CartApi:
    """购物车接口封装。"""

    CART_PATH = "/api/h5app/wxapp/cart"
    CART_DELETE_PATH = "/api/h5app/wxapp/cartdel"

    def __init__(self, client):
        self.client = client

    def add_to_cart(self, authorization, cart_data):
        return self.client.post(
            self.CART_PATH,
            json=cart_data,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": authorization,
            },
        )

    def list_cart(self, authorization, shop_type, company_id):
        return self.client.get(
            f"{self.CART_PATH}/list",
            params={
                "shop_type": shop_type,
                "company_id": company_id,
            },
            headers={
                "Accept": "application/json",
                "Authorization": authorization,
            },
        )

    def delete_cart(self, authorization, cart_id, company_id):
        return self.client.delete(
            self.CART_DELETE_PATH,
            json={
                "cart_id": cart_id,
                "company_id": company_id,
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": authorization,
            },
        )
