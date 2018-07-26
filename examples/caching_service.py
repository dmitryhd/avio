#!/usr/bin/env python3

from aiohttp import web
from avio import ProtoAppBuilder, run_app, app_logger
from avio import ApiHandler
from avio import JsonApiClient
from avio.clients.redis_client import CacheRedisClient


class ItemClient(JsonApiClient):

    NAME = 'item_client'
    default_config = {
        'url': '',
        'timeout_seconds': 1,
        'conn_limit': 100,
    }


class AppHandler(ApiHandler):

    @property
    def item_client(self) -> ItemClient:
        return self.app[ItemClient.NAME]

    @property
    def cache_client(self) -> CacheRedisClient:
        return self.app[CacheRedisClient.NAME]


class ItemHandler(AppHandler):

    async def get(self):
        _id = self.request.query.get('id', 1)
        data = await self.cache_client.get(_id)
        if data:
            self.metrics_buffer.incr('cache_hit')
            return self.finalize(data)
        else:
            self.metrics_buffer.incr('cache_miss')
        res = await self.item_client.get('')
        data = res.json
        print('data1', data)
        if data:
            await self.cache_client.setex(_id, data)
        print('data2', data)
        return self.finalize(data)


class AppBuilder(ProtoAppBuilder):

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
        self.register_clients(
            app,
            ItemClient,
            CacheRedisClient,
        )


def main():
    builder = AppBuilder()
    app = builder.build_app()
    run_app(app)


if __name__ == '__main__':
    # PYTHONPATH='.' python3 ./examples/simplest_service.py
    main()
