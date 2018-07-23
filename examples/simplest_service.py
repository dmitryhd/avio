#!/usr/bin/env python3

from aiohttp import web
from avio import AppBuilder, run_app, app_logger
from avio import ApiHandler
from avio import JsonApiClient


# TODO: make client as part of applicatoin???
async def create_cli(app: web.Application):
    app_logger.debug('client created')
    app['item_client'] = JsonApiClient(**app['config']['item_client'])


async def dispose_cli(app: web.Application):
    if 'item_client' in app:
        app_logger.debug('client deleted')
        await app['item_client'].close()
        del app['item_client']


class ItemHandler(ApiHandler):

    @property
    def item_client(self) -> JsonApiClient:
        return self.app['item_client']

    async def get(self):
        res = await self.item_client.get('')
        return self.finalize({
            'item': res.json
        })


class ExampleAppBuilder(AppBuilder):

    additional_config = {
        'item_client': {
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

        app.on_startup.append(create_cli)
        app.on_cleanup.append(dispose_cli)


def main():
    builder = ExampleAppBuilder()
    app = builder.build_app()
    run_app(app)


if __name__ == '__main__':
    # PYTHONPATH='.' python3 ./examples/simplest_service.py
    main()
