import pytest
from aiohttp import web

from avio import application


def get_test_app() -> web.Application:
    config = {}
    return application.make_app(config=config)


@pytest.fixture
def cli(loop, aiohttp_client):
    # Enable debug output
    loop.set_debug(True)
    app = get_test_app()
    return loop.run_until_complete(aiohttp_client(app))
