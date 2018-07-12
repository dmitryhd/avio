import time

from aiohttp import web
import socket
import asyncio
import uvloop
from copy import deepcopy
from typing import Optional

import avio.log as log
import avio.default_middleware as default_middleware
import avio.default_handlers as default_handlers
from avio.config import ConfigParser
from avio.metrics import _create_metrics_sender, _dispose_metrics_sender


class AppBuilder:

    def __init__(self, app_config: Optional[dict] = None):
        """
        Possible config options: str, dict, none
        """
        self.app_config = app_config or {}
        self._base_config = self._get_config()
        self._logger = log.app_logger
        self.middlewares = [
            default_middleware.format_exceptions,
            default_middleware.measure_time_and_send_metrics,
        ]

    def _get_config(self) -> dict:
        config_parser = ConfigParser(self.default_config)
        config_parser.update_config(self.app_config)
        return config_parser.read_config()

    @property
    def default_config(self) -> dict:
        return {
            'logging': {
            },
            'image_tag': 'dev',  # Unique id
            'enable_jsonchema': False,
            'debug': False,
            'host': '0.0.0.0',
            'port': 8890,
            'metrics': {
                'host': 'localhost',
                'port': 8125,
                'prefix': 'apps.services.avio',
                'enabled': True,
            },
            'ioloop_type': 'uvloop',
            'shutdown_timeout_seconds': 2.0,
        }

    @staticmethod
    def _setup_default_routes(app: web.Application):
        app.router.add_view('/_info', default_handlers.InfoHandler, name='info')
        app.router.add_view('/_error', default_handlers.ErrorHandler, name='error')
        app.router.add_view('/_echo', default_handlers.EchoHandler, name='echo')
        app.router.add_view('/_info_detailed', default_handlers.DetailedInfoHandler, name='info_detailed')

    def prepare_app(self, app: web.Application, config: dict = None):
        """
        Modify app before being build.
        Change config, modify callbacks, add routes.
        Should modify app inplace, returns None.
        """
        return

    def _setup_logger(self, config: dict):
        self._logger = log.configure_app_logger(logger_config=config.get('logging'))

    def _setup_event_loop(self, config: dict):
        if config.get('ioloop_type') == 'uvloop':
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            self._logger.info('Using uvloop')
        else:
            self._logger.info('Using default asyncio loop')

    def _update_config(self, new_config: dict = None) -> dict:
        """:return: copy of local config, updated with new_config"""
        return ConfigParser.update(self._base_config, new_config)

    @staticmethod
    def _add_default_contexts(app: web.Application):
        app.on_startup.append(_create_metrics_sender)
        app.on_cleanup.append(_dispose_metrics_sender)

    def build_app(self, new_config: Optional[dict] = None) -> web.Application:
        """
        Creates application.
        If config dict not specified, yaml file in env CONFIG_PAT will be readed, else empty config passed
        """
        config = self._update_config(new_config)

        self._setup_logger(config)
        self._setup_event_loop(config)

        app = web.Application(middlewares=self.middlewares)
        app['config'] = deepcopy(config)
        app['start_ts'] = time.time()

        self._setup_default_routes(app)
        self._add_default_contexts(app)

        self.prepare_app(app, config)

        return app

    def run_app(self, app=None, new_config: Optional[dict] = None):
        if not app:
            app = self.build_app(new_config)
        port = app['config'].get('port', 8890)
        log.app_logger.warn(f'Service running at http://{socket.gethostname()}:{port}')
        web.run_app(
            app,
            host=app['config'].get('host', '0.0.0.0'),
            port=port,
            shutdown_timeout=app['config'].get('shutdown_timeout_seconds', 2.0),
            print=False,
            # TODO: separate access logger
            access_log=log.app_logger,
        )

# https://aiohttp.readthedocs.io/en/stable/web_quickstart.html#organizing-handlers-in-classes
# https://stackoverflow.com/questions/32819231/
# class-based-views-in-aiohttp?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qahello
# The code doesn't recreate BaseView for every request
# https://aiohttp.readthedocs.io/en/stable/web_advanced.html#middlewares
