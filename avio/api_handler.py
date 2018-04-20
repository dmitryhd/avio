import time
import logging
from contextlib import contextmanager

from aiohttp import web

import avio.log as log


class ApiHandler(web.View):
    TIMER_PRECISION = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timers = {}  # Timer name -> seconds passed

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

    @contextmanager
    def timeit(self, timer_name: str):
        start_ts = time.time()
        yield
        end_ts = time.time()
        self.timers[timer_name] = round(end_ts - start_ts, self.TIMER_PRECISION)
