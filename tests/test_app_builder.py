from aiohttp import web

from avio.app_builder import ProtoAppBuilder
from avio.default_handlers import InfoHandler


def test_create_app():
    app = ProtoAppBuilder().build_app()
    assert isinstance(app, web.Application)


def test_app_config():
    builder = ProtoAppBuilder({'app_key': 'value'})
    app = builder.build_app({'update_key': 'value'})
    config = app['config']
    assert 'value' == config['app_key']
    assert 'value' == config['update_key']
    assert 'logging' in config
    assert 'host' in config
    assert 'port' in config
    assert 'ioloop_type' in config


def test_app_routes():
    builder = ProtoAppBuilder()
    app = builder.build_app()
    assert 'info' in app.router.named_resources()
    assert 'error' in app.router.named_resources()


def test_additional_routes():

    class MyAppBuilder(ProtoAppBuilder):

        def prepare_app(self, app: web.Application, config: dict = None):
            app.router.add_view('/_info2', InfoHandler, name='info2')

    builder = MyAppBuilder()
    app_ = builder.build_app()
    assert 'info2' in app_.router.named_resources()
