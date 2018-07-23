import time
import logging
from contextlib import contextmanager

from aiohttp import web

import avio.log as log
from avio.metrics import MetricsBuffer


class ApiHandler(web.View):
    """
    Address self.request to get app.
    """
    TIMER_PRECISION = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def timers(self) -> dict:
        return self.request.timers

    @property
    def metrics_buffer(self) -> MetricsBuffer:
        return self.request.metrics_buffer

    @property
    def app(self) -> web.Application:
        return self.request.app

    @property
    def log(self) -> logging.Logger:
        return log.app_logger

    @property
    def config(self) -> dict:
        # TODO: mb make it read only?)
        return self.request.app['config']

    async def request_json(self) -> dict:
        # TODO: scheme validation goes here
        return await self.request.json()

    def finalize(self, response: dict) -> web.Response:
        """
        Serializes response
        """
        return web.json_response(response)

    @contextmanager
    def timeit(self, timer_name: str):
        start_ts = time.time()
        yield
        end_ts = time.time()
        self.timers[timer_name] = round(end_ts - start_ts, self.TIMER_PRECISION)
