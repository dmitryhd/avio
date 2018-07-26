import json
import asyncio
from typing import Optional

import aioredis
from aiohttp import web
from async_timeout import timeout

from avio.clients.client import Client


class RedisClient(Client):
    """
    see:
    - https://github.com/aio-libs/aioredis
    - http://aioredis.readthedocs.io/en/v1.1.0/
    """

    NAME = 'redis'
    default_config = {
        'host': 'localhost',
        'port': 6379,
        'conn_timeout': 1,
        'op_timeout': .5,
        'db': 0,
        'pool_size': 2,
    }

    redis_pool: aioredis.ConnectionsPool

    def __init__(self, **kwargs):
        self.redis_pool = None
        self._op_timeout = kwargs.get('op_timeout')  # None will disable timeout

    async def close(self):
        self.redis_pool.close()
        await self.redis_pool.wait_closed()

    @classmethod
    async def from_app(cls, app: web.Application):
        """
        :return: instance of client, configured from config in application
        """
        cfg = cls.get_config(app)

        client = cls(**cfg)
        client.config = cfg
        pool = await aioredis.create_pool(
            (cfg['host'], cfg['port']),
            db=cfg['db'],
            loop=app.loop,
            maxsize=cfg['pool_size'],
            create_connection_timeout=cfg['conn_timeout'],
        )
        client.redis_pool = pool
        return client

    async def execute(self, command, *args, **kw):
        """
        :raises: TimeoutError
        """
        with timeout(self._op_timeout):
            return await self.redis_pool.execute(command, *args, **kw)

    async def set(self, key, val):
        return await self.execute('set', key, val)

    async def setex(self, key, val, ttl: float):
        return await self.execute('set', key, val, 'ex', ttl)

    async def get(self, key):
        return await self.execute('get', key)

    async def mget(self, keys):
        return await self.execute('get', *keys)


class CacheRedisClient(RedisClient):
    """
    Usage:
    ```python

    @property
    def cache_client(self) -> CacheRedisClient:
        return self.app[CacheRedisClient.NAME]


    class ItemHandler(AppHandler):

        async def get(self):
            _id = self.request.query.get('id', 1)

            data = await self.cache_client.get(_id)
            if data:
                app_logger.warn('HIT')
                return self.finalize(data)
            else:
                app_logger.warn('Miss')
            res = await self.item_client.get('')
            data = res.json
            if data:
                await self.cache_client.setex(_id, data)
            return self.finalize(data)
    ```
    """

    NAME = 'cache_redis_client'
    default_config = {
        'host': 'localhost',
        'port': 6379,
        'conn_timeout': 1,
        'op_timeout': .5,
        'db': 0,
        'pool_size': 2,
        'ttl_seconds': 5,
    }
    # TODO: hit/miss rate

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ttl_seconds = kwargs.get('ttl_seconds', 5)

    def serialize(self, data) -> Optional[bytes]:
        try:
            return json.dumps(data, ensure_ascii=False).encode('utf8')
        except (json.JSONDecodeError, TypeError):
            return None

    def deserialize(self, raw_data: bytes):
        if not raw_data:
            return None
        try:
            return json.loads(raw_data)
        except (json.JSONDecodeError, TypeError):
            return None

    async def get(self, key) -> Optional[dict]:
        try:
            raw_data = await super().get(key)
            deser = self.deserialize(raw_data)
            return deser
        except asyncio.TimeoutError:
            return None

    async def setex(self, key, val, ttl: float = 1):
        """
        This function returns immediately.
        Uses self.ttl_seconds.
        """
        raw_data = self.serialize(val)
        future = super().setex(key, raw_data, self.ttl_seconds)
        # Fire and forget coroutine
        asyncio.ensure_future(future, loop=self.redis_pool._loop)
