from aiohttp import web

from avio.app_builder import AppBuilder
from avio.default_handlers import InfoHandler



def test_create_app():
    app = AppBuilder().build_app()
    assert isinstance(app, web.Application)


def test_app_config():
    builder = AppBuilder({'app_key': 'value'})
    app = builder.build_app({'update_key': 'value'})
    config = app['config']
    assert 'value' == config['app_key']
    assert 'value' == config['update_key']
    assert 'logging' in config
    assert 'host' in config
    assert 'port' in config
    assert 'ioloop_type' in config


def test_app_routes():
    builder = AppBuilder()
    app = builder.build_app()
    assert 'info' in app.router.named_resources()
    assert 'error' in app.router.named_resources()


def test_additional_routes():

    class MyAppBuilder(AppBuilder):

        def prepare_app(self, app: web.Application, config: dict = None):
            app.router.add_view('/_info2', InfoHandler, name='info2')

    builder = MyAppBuilder()
    app = builder.build_app()
    assert 'info2' in app.router.named_resources()
