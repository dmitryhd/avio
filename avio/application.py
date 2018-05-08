import time

from aiohttp import web

import avio.log as log
import avio.default_middleware as default_middleware
import avio.default_handlers as default_handlers
from avio.config import get_config_from_env


def run_app(app):
    """
    Starts application server.
    Host and port specified in app['config'] dict
    """
    web.run_app(
        app,
        host=app['config'].get('app_host', '0.0.0.0'),
        port=app['config'].get('app_port', 8890),
    )


def setup_default_routes(app: web.Application):
    app.router.add_view('/_info', default_handlers.InfoHandler)
    app.router.add_view('/_error', default_handlers.ErrorHandler)
    app.router.add_view('/_echo', default_handlers.EchoHandler)
    app.router.add_view('/_info_detailed', default_handlers.DetailedInfoHandler)


def make_app(config: dict = None) -> web.Application:
    """
    Creates application.
    If config dict not specified, yaml file in env CONFIG_PAT will be readed, else empty config passed
    """
    app = web.Application(middlewares=[
        default_middleware.format_exceptions,
        default_middleware.measure_time,
    ])
    if not config:
        config = get_config_from_env()
    app['config'] = config
    app['start_ts'] = time.time()
    setup_default_routes(app)

    log.configure_app_logger(logger_config=config.get('logging'))
    return app


# https://aiohttp.readthedocs.io/en/stable/web_quickstart.html#organizing-handlers-in-classes
# https://stackoverflow.com/questions/32819231/
# class-based-views-in-aiohttp?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qahello
# The code doesn't recreate BaseView for every request
# https://aiohttp.readthedocs.io/en/stable/web_advanced.html#middlewares
