from copy import deepcopy

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
        cfg = deepcopy(cls.default_config) if cls.default_config else {}
        cfg = cfg.update(app['config'][cls.NAME])

        client = cls(**cfg)
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
