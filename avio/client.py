from aiohttp import web
from copy import deepcopy

from avio.log import app_logger


class Client:

    NAME = 'noname_client'
    default_config = {}
    config: dict = None

    @classmethod
    async def from_app(cls, app: web.Application):
        """
        :return: instance of client, configured from config in application
        """
        cfg = cls.get_config(app)
        instance = cls(**cfg)
        instance.config = cfg
        return instance

    @classmethod
    def get_config(cls, app) -> dict:
        cfg = deepcopy(cls.default_config) if cls.default_config else {}
        cfg.update(app['config'].get(cls.NAME, {}))
        return cfg

    @classmethod
    async def startup(cls, app: web.Application):
        """
        should be registered on
        app.on_startup.append(ItemClient.initialize)
        """

        if cls.NAME in app:
            app_logger.warn(f'{cls.NAME} already in app!')
            await cls.cleanup(app)

        instance = await cls.from_app(app)
        app[cls.NAME] = instance
        app_logger.debug(f'{instance} created')

    @classmethod
    async def cleanup(cls, app: web.Application):
        """
        should be registered on
        app.on_cleanup.append(ItemClient.cleanup)
        """

        if cls.NAME in app:
            await app[cls.NAME].close()
            del app[cls.NAME]
            app_logger.debug(f'{cls.NAME} deleted')

    async def close(self):
        app_logger.warn(f'{self.NAME} not implemented!')

    def __repr__(self) -> str:
        if self.config:
            cfg_str = ', '.join(f'{key}={val}' for key, val in self.config.items())
        else:
            cfg_str = ''
        return f'<{self.__class__.__name__}(name={self.NAME}, {cfg_str})>'

