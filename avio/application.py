from aiohttp import web


def make_app(config: dict = None, loop=None) -> web.Application:
    app = web.Application()
    setup_routes(app)
    return app


def run_app(config: dict, app):
    web.run_app(app, host='127.0.0.1', port=8080)


def setup_routes(app: web.Application):
    # app.router.add_get('/', index)
    pass


