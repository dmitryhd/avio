import traceback

from aiohttp import web

import avio.default_handlers as default_handlers
from avio.config import get_config_from_env


def run_app(app):
    web.run_app(
        app,
        host=app['config'].get('app_host', '0.0.0.0'),
        port=app['config'].get('app_port', 8890),
    )


def setup_default_routes(app: web.Application):
    app.router.add_view('/_info', default_handlers.InfoHandler)
    app.router.add_view('/_error', default_handlers.ErrorHandler)


UNHANDLED_ERROR_MESSAGE = 'Wild error occured!'


@web.middleware
async def format_exceptions(request, handler):
    """
    Middleware, that leaves responses, that don't raise exceptions unchanged.

    Converts all errors to common format, containing
    - http error code
    - human readable message
    - traceback

    NOTE: on json handling https://aiohttp.readthedocs.io/en/stable/web_advanced.html#example
    """

    status = 200
    message = ''
    traceback_str = ''
    try:
        # If no exception raised - return response straight away
        return await handler(request)

    # Jsonify any http exception on wrong url
    except web.HTTPException as ex:
        status = ex.status
        traceback_str = traceback.format_exc()
        message = ex.reason

    except Exception:
        status = 500
        traceback_str = traceback.format_exc()
        message = UNHANDLED_ERROR_MESSAGE

    response = {
        'code': status,
        'message': message,
        'traceback': traceback_str,  # TODO: make traceback optional
    }
    # TODO: mb handle ensure json
    return web.json_response(response, status=status)


def make_app(config: dict = None) -> web.Application:
    """
    Creates application.
    If config dict not specified, yaml file in env CONFIG_PAT will be readed, else empty config passed
    """
    app = web.Application(middlewares=[format_exceptions])
    if not config:
        config = get_config_from_env()
    app['config'] = config
    setup_default_routes(app)
    return app

# https://aiohttp.readthedocs.io/en/stable/web_quickstart.html#organizing-handlers-in-classes
# https://stackoverflow.com/questions/32819231/
# class-based-views-in-aiohttp?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qahello
# The code doesn't recreate BaseView for every request

# https://aiohttp.readthedocs.io/en/stable/web_advanced.html#middlewares
