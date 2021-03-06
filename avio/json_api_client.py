"""
how to trace clients
# https://docs.aiohttp.org/en/stable/client_advanced.html#client-tracing

"""

import time

import attr
import aiohttp
import async_timeout
from yarl import URL


TIMEOUT_CODE = 599


def get_session(limit=100, ttl_dns_cache=10, use_dns_cache=True, loop=None) -> aiohttp.ClientSession:
    """
    https://docs.aiohttp.org/en/stable/client_reference.html
    :return: properly configured tcp/http session with
    - asyncronous dns resolving enabled
    - dns cache enabled with proper timeout
    - connections limited
    - timeouts set
    """
    conn = aiohttp.TCPConnector(
        limit=limit,
        ttl_dns_cache=ttl_dns_cache,
        use_dns_cache=use_dns_cache,
        loop=loop,
    )
    # aiohttp.DefaultResolver by default (asynchronous if aiodns>=1.1 is installed).
    return aiohttp.ClientSession(connector=conn)


@attr.s
class ApiResponse:
    status = attr.ib(default=200)
    json = attr.ib(default=attr.Factory(dict))
    is_timeouted = attr.ib(default=False)
    seconds_run = attr.ib(default=0)


class JsonApiClient:
    """
    Client for json api.
    Http transport is used.
    All parameters passed by post request are json.
    All responses are json.
    return values are ApiResponse objects (have status and json fields)
    """

    def __init__(self,
                 base_url: str,
                 session: aiohttp.ClientSession = None,
                 timeout_seconds: float = None):
        self._base_url = URL(base_url)
        self._session = session or get_session()
        self._timeout_seconds = timeout_seconds

    async def _fetch(self, future) -> ApiResponse:
        response = ApiResponse(status=TIMEOUT_CODE, is_timeouted=True)
        btime = time.time()
        async with async_timeout.timeout(self._timeout_seconds, loop=self.loop):
            async with future as resp:
                response.status = resp.status
                # Note: treat all mime types as json
                response.json = await resp.json(content_type=None)
                response.is_timeouted = False
        response.seconds_run = time.time() - btime
        return response

    async def get(self, path: str) -> ApiResponse:
        url = self._path_to(path)
        future = self._session.get(url)
        return await self._fetch(future)

    async def post(self, path: str, json: dict) -> ApiResponse:
        url = self._path_to(path)
        future = self._session.post(url, json=json)
        return await self._fetch(future)

    @property
    def loop(self):
        return self._session._loop

    def _path_to(self, path: str) -> str:
        return self._base_url.join(URL(path)).human_repr()

    def __repr__(self) -> str:
        return f'<JsonApiClient(\'{self._base_url}\')>'
