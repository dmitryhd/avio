from aiohttp import web
from avio import application


def test_create_app(loop):
    app = application.make_app(loop=loop)
    assert isinstance(app, web.Application)
