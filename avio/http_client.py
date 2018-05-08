"""
how to trace clients
# https://docs.aiohttp.org/en/stable/client_advanced.html#client-tracing

"""

import aiohttp


class HttpClient:
    def __init__(self):
        self._session = aiohttp.ClientSession()

    async def get_json(self, url: str) -> dict:
        async with self._session.get(url) as resp:
            # assert resp.status == 200
            return await resp.text()
