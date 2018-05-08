"""
how to trace clients
# https://docs.aiohttp.org/en/stable/client_advanced.html#client-tracing

"""

from collections import namedtuple

from yarl import URL
import aiohttp


ApiResponse = namedtuple('HttpResponse', 'status, json')


class JsonApiClient:

    def __init__(self, base_url: str, session: aiohttp.ClientSession = None):
        self._base_url = URL(base_url)
        self._session = session or aiohttp.ClientSession()

    async def get(self, path: str) -> ApiResponse:
        """
        This method should never rise exceptions
        :return: named tuple(status, data). Data should be dict. May be empty
        """
        url = self._path_to(path)
        async with self._session.get(url) as resp:
            response_json = await resp.json()
            return ApiResponse(resp.status, response_json)

    async def post(self, path: str, json: dict) -> ApiResponse:
        """
        This method should never rise exceptions
        :return: named tuple(status, data). Data should be dict. May be empty
        """
        url = self._path_to(path)
        async with self._session.post(url, json=json) as resp:
            response_json = await resp.json()
            return ApiResponse(resp.status, response_json)

    def _path_to(self, path: str) -> str:
        return self._base_url.join(URL(path)).human_repr()

    def __repr__(self) -> str:
        return f'<JsonApiClient(\'{self._base_url}\')>'
