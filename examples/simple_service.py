#!/usr/bin/env python3

import asyncio

from aiohttp import web
from avio import AppBuilder, run_app, app_logger
from avio import ApiHandler


class ItemHandler(ApiHandler):

    async def get(self):
        await asyncio.sleep(0.1)
        return self.finalize({'data': 100})


class ExampleAppBuilder(AppBuilder):

    additional_config = {
        'logging': {'level': 'DEBUG'},
        'debug': True,
        'port': 8891,
    }

    def prepare_app(self, app: web.Application, config: dict = None):
        app.router.add_view('/item', ItemHandler, name='item')


def main():
    builder = ExampleAppBuilder()
    app = builder.build_app()
    run_app(app)


if __name__ == '__main__':
    # PYTHONPATH='.' python3 ./examples/simplest_service.py
    main()
