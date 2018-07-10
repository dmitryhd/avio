from avio import statsd


def test_format_metric():
    buf = statsd.StatsdBuffer(prefix='prefix')
    assert [] == buf.data
    buf.incr('m1', 1)
    assert ['prefix.m1:1|c\n'] == buf.data
    buf.incr('m2', 2)
    assert ['prefix.m1:1|c\n', 'prefix.m2:2|c\n'] == buf.data
    assert b'prefix.m1:1|c\nprefix.m2:2|c\n' == buf.to_bytes


async def test_statsd_client(loop):
    buf = statsd.StatsdBuffer(prefix='prefix')
    client = statsd.StatsdClient(loop=loop)
    await client.send_buffer(buf)

