import traceback

from aiohttp import web


def run_app(config: dict, app):
    web.run_app(app, host='127.0.0.1', port=8080)


def setup_routes(app: web.Application):
    app.router.add_view('/_info', InfoHandler)
    app.router.add_view('/_error', ErrorHandler)


class InfoHandler(web.View):

    async def get(self):
        info = {'result': 'ok'}
        return web.json_response(info)


class ErrorHandler(web.View):

    async def get(self):
        raise Exception('Somebody activated _error handler')


@web.middleware
async def convert_errors_to_json(request, handler):
    try:
        return await handler(request)
    except Exception as e:
        tb = traceback.format_exc()
        error = {'error': tb}
        return web.json_response(error, status=500)


def make_app(config: dict = None, loop=None) -> web.Application:
    app = web.Application(middlewares=[convert_errors_to_json])
    setup_routes(app)
    return app

# https://aiohttp.readthedocs.io/en/stable/web_quickstart.html#organizing-handlers-in-classes
# https://stackoverflow.com/questions/32819231/
# class-based-views-in-aiohttp?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qahello
# The code doesn't recreate BaseView for every request

# https://aiohttp.readthedocs.io/en/stable/web_advanced.html#middlewares
