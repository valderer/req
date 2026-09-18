class AddressApi:
    """地址相关接口封装。"""

    ADDRESS_PATH = "/api/h5app/wxapp/member/address"
    ADDRESS_LIST_PATH = "/api/h5app/wxapp/member/addresslist"

    def __init__(self, client):
        self.client = client

    def add_address(self, authorization, address_data):
        return self.client.post(
            self.ADDRESS_PATH,
            json=address_data,
            headers=self._json_headers(authorization),
        )

    def query_addresses(self, authorization, company_id):
        return self.client.get(
            self.ADDRESS_LIST_PATH,
            params={"company_id": company_id},
            headers={
                "Accept": "application/json",
                "Authorization": authorization,
            },
        )

    def delete_address(self, authorization, company_id, address_id):
        return self.client.request(
            "DELETE",
            f"{self.ADDRESS_PATH}/{address_id}",
            json={"company_id": company_id},
            headers=self._json_headers(authorization),
        )

    @staticmethod
    def _json_headers(authorization):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": authorization,
        }
