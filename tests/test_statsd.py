from avio import statsd


def test_buffer_format_metric():
    buf = statsd.StatsdBuffer(prefix='prefix')
    assert [] == buf.data
    buf.incr('m1', 1)
    assert ['prefix.m1:1|c\n'] == buf.data
    buf.incr('m2', 2)
    assert ['prefix.m1:1|c\n', 'prefix.m2:2|c\n'] == buf.data
    assert b'prefix.m1:1|c\nprefix.m2:2|c\n' == buf.to_bytes


def test_buffer_extend():
    buf = statsd.StatsdBuffer()
    buf.incr('m1', 1)
    buf.incr('m2', 2)
    assert b'.m1:1|c\n.m2:2|c\n' == buf.to_bytes
    buf2 = statsd.StatsdBuffer()
    buf2.incr('m3', 1)
    buf.extend(buf2)
    assert b'.m1:1|c\n.m2:2|c\n.m3:1|c\n' == buf.to_bytes


async def test_statsd_client(loop):
    buf = statsd.StatsdBuffer(prefix='prefix')
    client = statsd.StatsdClient(loop=loop)
    await client.send_buffer(buf)


async def test_statsd_info(cli):
    resp = await cli.get('/_info')
    payload = await resp.json()
    assert {'result': 'ok'} == payload
    assert resp.status == 200
