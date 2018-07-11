import pytest
from aiohttp import web

from avio import application
from avio.metrics import DummyMetricsSender


def get_test_app() -> web.Application:
    config = {}
    return application.make_app(config=config)


@pytest.fixture
def cli(loop, aiohttp_client):
    # Enable debug output
    loop.set_debug(True)
    app = get_test_app()
    app['metrics_sender'] = DummyMetricsSender(loop=loop)
    return loop.run_until_complete(aiohttp_client(app))
