from aiohttp import web
from copy import deepcopy

from avio.log import app_logger


class Client:
    NAME = 'noname_client'
    default_config = {}

    @classmethod
    async def from_app(cls, app: web.Application):
        """
        :return: instance of client, configured from config in application
        """
        cfg = deepcopy(cls.default_config) if cls.default_config else {}
        cfg = cfg.update(app['config'][cls.NAME])
        return cls(**cfg)

    @classmethod
    async def startup(cls, app: web.Application):
        """
        should be registered on
        app.on_startup.append(ItemClient.initialize)
        """

        if cls.NAME in app:
            app_logger.warn(f'{cls.NAME} already in app!')
            await cls.cleanup(app)

        app_logger.debug(f'{cls.NAME} created')
        app[cls.NAME] = cls.from_app(app)

    @classmethod
    async def cleanup(cls, app: web.Application):
        """
        should be registered on
        app.on_cleanup.append(ItemClient.cleanup)
        """

        if cls.NAME in app:
            app_logger.debug(f'{cls.NAME} deleted')
            await app[cls.NAME].close()
            del app[cls.NAME]

    async def close(self):
        app_logger.warn(f'{self.NAME} not implemented!')

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(name={self.NAME})>'

