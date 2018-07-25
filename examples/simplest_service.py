#!/usr/bin/env python3

from aiohttp import web
from avio import AppBuilder, run_app, app_logger
from avio import ApiHandler
from avio import JsonApiClient


class ItemClient(JsonApiClient):
    NAME = 'item_client'
    default_config = {
        'url': '',
        'timeout_seconds': 1,
        'conn_limit': 100,
    }


class ItemHandler(ApiHandler):

    @property
    def item_client(self) -> ItemClient:
        return self.app[ItemClient.NAME]

    async def get(self):
        res = await self.item_client.get('')
        return self.finalize({
            'item': res.json
        })


class ExampleAppBuilder(AppBuilder):

    additional_config = {
        ItemClient.NAME: {
            'url': 'http://localhost:8891/item',
            'timeout_seconds': .5,
        },
        'logging': {
            'level': 'DEBUG',
        },
        'debug': True,
    }

    def prepare_app(self, app: web.Application, config: dict = None):
        app.router.add_view('/item', ItemHandler, name='item')

        app.on_startup.append(ItemClient.startup)
        app.on_cleanup.append(ItemClient.cleanup)


def main():
    builder = ExampleAppBuilder()
    app = builder.build_app()
    run_app(app)


if __name__ == '__main__':
    # PYTHONPATH='.' python3 ./examples/simplest_service.py
    main()
