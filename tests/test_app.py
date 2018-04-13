from aiohttp import web
import pytest

from avio import application


def test_create_app():
    app = application.make_app()
    assert isinstance(app, web.Application)


def get_test_app() -> web.Application:
    config = {}
    return application.make_app(config=config)


@pytest.fixture
def cli(loop, aiohttp_client):
    # Enable debug output
    loop.set_debug(True)
    app = get_test_app()
    return loop.run_until_complete(aiohttp_client(app))


async def test_info(cli):
    resp = await cli.get('/_info')
    payload = await resp.json()
    assert {'result': 'ok'} == payload
    assert resp.status == 200


async def test_error_handler(cli):
    response = await cli.get('/_error')
    response_json = await response.json()

    assert 500 == response.status
    assert 500 == response_json['code']
    assert application.UNHANDLED_ERROR_MESSAGE == response_json['message']
    assert response_json['traceback'].startswith('Traceback (most recent call last):\n  File')


async def test_page_not_found(cli):
    resp = await cli.get('/some-strange-url')
    assert resp.status == 404
    payload = await resp.json()
    assert 404 == payload['code']
    assert 'Not Found' == payload['message']

# TODO: test return unicode json in response
