import json
import asyncio
from typing import Optional

import aioredis
from aiohttp import web
from async_timeout import timeout

from avio.client import Client


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

    async def get(self, key) -> Optional[dict]:
        try:
            data = await super().get(key)
            return json.loads(data)
        except asyncio.TimeoutError:
            return None
        except (json.JSONDecodeError, TypeError):
            return None

    async def setex(self, key, val, ttl: float = 1):
        if isinstance(val, list) or isinstance(val, dict):
            val = json.dumps(val, ensure_ascii=False)
        future = super().setex(key, val, self.ttl_seconds)
        # Fire and forget!
        asyncio.ensure_future(future, loop=self.redis_pool._loop)
