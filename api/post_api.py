class PostApi:
    """JSONPlaceholder 的文章接口。"""

    def __init__(self, client):
        self.client = client

    def get_post(self, post_id: int):
        return self.client.get(f"/posts/{post_id}")
