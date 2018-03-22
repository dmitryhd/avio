from aiohttp import web
from avio import application


def test_create_app(loop):
    app = application.make_app(loop=loop)
    assert isinstance(app, web.Application)


def get_test_app(loop) -> web.Application:
    # Enable debug output
    loop.set_debug(True)
    return application.make_app(loop=loop)


async def test_info(test_client):
    client = await test_client(get_test_app)

    resp = await client.get('/_info')
    payload = await resp.json()
    assert {'result': 'ok'} == payload
    assert resp.status == 200


async def test_error(test_client):
    client = await test_client(get_test_app)

    resp = await client.get('/_error')
    assert resp.status == 500

    payload = await resp.json()
    assert 'error' in payload
    assert payload['error'].startswith('Traceback (most recent call last):\n  File')
