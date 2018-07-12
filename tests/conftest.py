import pytest
from aiohttp import web

from avio.app_builder import AppBuilder
from avio.metrics import DummyMetricsSender


@pytest.fixture
def test_app() -> web.Application:
    config = {}
    app_builder = AppBuilder()
    app = app_builder.build_app(config)
    return app


@pytest.fixture
def cli(loop, aiohttp_client, test_app):
    # Enable debug output
    loop.set_debug(True)
    test_app['metrics_sender'] = DummyMetricsSender(loop=loop)
    return loop.run_until_complete(aiohttp_client(test_app))
