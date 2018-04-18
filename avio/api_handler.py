import logging

from aiohttp import web

import avio.log as log


class ApiHandler(web.View):

    @property
    def app(self) -> web.Application:
        return self.request.app

    @property
    def log(self) -> logging.Logger:
        return log.app_logger

    @property
    def config(self) -> dict:
        # TODO: mb make it read only?)
        return self.app['config']

    # TODO: time measure goes here

    async def request_json(self) -> dict:
        # TODO: scheme validation goes here
        return await self.request.json()

    def finalize(self, response: dict):
        return web.json_response(response)
