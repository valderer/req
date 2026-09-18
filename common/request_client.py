import time

import requests

from common.logger import get_logger


logger = get_logger(__name__)


class RequestClient:
    """对 requests 做一层很薄的封装，方便统一管理基础地址和超时。"""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        start = time.perf_counter()
        try:
            response = requests.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException:
            elapsed = time.perf_counter() - start
            logger.exception("%s %s failed (%.3fs)", method.upper(), url, elapsed)
            raise

        elapsed = time.perf_counter() - start
        logger.info(
            "%s %s -> HTTP %s (%.3fs)",
            method.upper(),
            url,
            response.status_code,
            elapsed,
        )
        return response

    def get(self, path: str, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self.request("DELETE", path, **kwargs)
