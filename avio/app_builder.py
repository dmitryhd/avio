import time
from copy import deepcopy
from typing import Optional
import socket

import yaml
import asyncio
import uvloop
from aiohttp import web

import avio.log as log
import avio.middleware as middleware
import avio.default_handlers as default_handlers
import avio.config as cfg
from avio.metrics import create_metrics_sender, dispose_metrics_sender
from avio.sentry import configure_sentry, dispose_sentry


class ProtoAppBuilder:
    """
    Usage:
    customization: just inherit me and overwrite self.prepare_app
    >>> builder = ProtoAppBuilder({'connections': 100})
    >>> app = builder.build_app({'custom_setting': 1})
    """
    additional_config: dict = {}

    _default_config: dict = {
        'logging': {
            'level': 'WARN',
            'tag': 'tag_not_set',
            'access_level': 'WARN',
            'sentry_enabled': False,
            'sentry_dsn': '',
            'sentry_concurrent': 2,
            'sentry_enable_breadcrumbs': False,
            'sentry_level': 'WARN',
            'sentry_transport': 'queued',
            'sentry_transport_workers': 2,
            'sentry_transport_queue_size': 500,
        },
        'image_tag': 'dev',  # Unique id
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

    def __init__(self, app_config: Optional[dict] = None):
        #TODO: mb refactor config updates?
        config_parser = cfg.ConfigParser(self._default_config)
        self._base_config = config_parser.read_config()
        self._base_config = cfg.update(self._base_config, self.additional_config)
        self._base_config = cfg.update(self._base_config, app_config)

        self._logger = log.app_logger
        self.middlewares = [
            middleware.format_exceptions,
            middleware.measure_time_and_send_metrics,
        ]
        self.client_classes = []

    def build_app(self, new_config: Optional[dict] = None) -> web.Application:
        """
        Creates application.
        If config dict not specified, yaml file in env CONFIG_PAT will be readed, else empty config passed
        """
        config = cfg.update(self._base_config, new_config)

        self._setup_logger(config)
        self._setup_event_loop(config)

        app = web.Application(middlewares=self.middlewares)
        app['config'] = deepcopy(config)
        app['start_ts'] = time.time()

        self._setup_default_routes(app)
        self._add_default_contexts(app)

        self.prepare_app(app, config)

        return app

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

    @staticmethod
    def _add_default_contexts(app: web.Application):
        app.on_startup.append(create_metrics_sender)
        app.on_cleanup.append(dispose_metrics_sender)

        app.on_startup.append(configure_sentry)
        app.on_cleanup.append(dispose_sentry)

    @staticmethod
    def register_clients(app, *clients_classes):
        """
        usage:
        ```python
        self.register_clients(
            app,
            ItemClient,
            CacheRedisClient,
        )
        ```
        """
        for client_class in clients_classes:
            app.on_startup.append(client_class.startup)
            app.on_cleanup.append(client_class.cleanup)


def run_app(app: web.Application):
    port = app['config'].get('port', 8890)
    log.app_logger.warn(f'Service running at http://{socket.gethostname()}:{port}')
    web.run_app(
        app,
        host=app['config'].get('host', '0.0.0.0'),
        port=port,
        shutdown_timeout=app['config'].get('shutdown_timeout_seconds', 2.0),
        print=False,
        # TODO: separate access logger
        access_log=log.access_logger,
    )


def print_config_yaml(app: web.Application):
    config = app['config']
    for client_name in app.get('client_names', []):
        config[client_name] = app[client_name].config
        print(app[client_name].config)
    print(yaml.dump(config, default_flow_style=False))
