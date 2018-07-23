from aiohttp import web

from avio.log import app_logger


class Client:
    NAME = 'noname_client'

    @classmethod
    def from_app(cls, app: web.Application):
        return cls(**app['config'][cls.NAME])

    @classmethod
    async def initialize(cls, app: web.Application):

        if 'item_client' in app:
            app_logger.warn(f'{cls.NAME} already in app!')
            await cls.destroy(app)

        app_logger.debug(f'{cls.NAME} created')
        app[cls.NAME] = cls.from_app(app)

    @classmethod
    async def destroy(cls, app: web.Application):
        if 'item_client' in app:
            app_logger.debug(f'{cls.NAME} deleted')
            await app[cls.NAME].close()
            del app[cls.NAME]

    async def close(self):
        app_logger.warn(f'{self.NAME} not implemented!')

