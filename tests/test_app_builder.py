from aiohttp import web

from avio.app_builder import AppBuilder


def test_create_app():
    app = AppBuilder().build_app()
    assert isinstance(app, web.Application)
