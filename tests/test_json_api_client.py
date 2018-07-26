import pytest

from avio.clients import json_api_client as api_client


@pytest.fixture()
def test_api_client(cli):
    base_url = cli.make_url('').human_repr()
    client = api_client.JsonApiClient(base_url, cli.session)
    return client


async def test_get(test_api_client):
    resp = await test_api_client.get('/_info')
    assert isinstance(resp, api_client.ApiResponse)
    assert {'result': 'ok'} == resp.json
    assert resp.status == 200
    assert not resp.is_timeouted
    assert 1 > resp.seconds_run > 0


async def test_repr(test_api_client):
    assert 'api_client' in str(test_api_client)


async def test_error(test_api_client):
    resp = await test_api_client.get('/_error')
    assert 500 == resp.status
    assert 500 == resp.json['code']


async def test_404(test_api_client):
    resp = await test_api_client.get('/some-strange-url/')
    assert resp.status == 404
    assert 404 == resp.json['code']
    assert 'Not Found' == resp.json['message']


async def test_post(test_api_client):
    post_body = {'some_key': 'some_val даже с utf8'}

    response = await test_api_client.post(path='/_echo', json=post_body)
    assert 200 == response.status
    assert post_body == response.json
