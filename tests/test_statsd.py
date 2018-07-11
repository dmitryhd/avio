from avio import metrics


def test_buffer_format_metric():
    buf = metrics.MetricsBuffer()
    assert [] == buf.data
    buf.incr('m1', 1)
    assert [b'm1:1|c\n'] == buf.data
    buf.incr('m2', 2)
    assert [b'm1:1|c\n', b'm2:2|c\n'] == buf.data


def test_buffer_extend():
    buf = metrics.MetricsBuffer()
    buf.incr('m1', 1)
    buf.incr('m2', 2)
    assert [b'm1:1|c\n', b'm2:2|c\n'] == buf.data
    msg_len = 7
    assert 2 * msg_len == len(buf)
    buf2 = metrics.MetricsBuffer()
    buf2.incr('m3', 1)
    buf.extend(buf2)
    assert msg_len == len(buf2)
    assert [b'm1:1|c\n', b'm2:2|c\n', b'm3:1|c\n'] == buf.data
    assert 3 * msg_len == len(buf)


def test_buffer_split_to_packets_trivial():
    buf = metrics.MetricsBuffer()
    buf.incr('m1', 1)
    assert [b'prefix.m1:1|c\n'] == buf.split_to_packets(prefix='prefix')

def test_buffer_split_to_packets_long_prefix():
    buf = metrics.MetricsBuffer()
    buf.incr('m1', 1)
    prefix = b'some.freaking.long.prefix.common.for.' + b'.'.join([b'a'] * 100)

    assert [prefix + b'.m1:1|c\n'] == buf.split_to_packets(prefix=prefix + b'.')


def test_buffer_split_to_packets_two_messages():
    buf = metrics.MetricsBuffer()
    buf.incr('m1', 1)
    buf.incr('m2', 1)
    assert [b'prefix.m1:1|c\nprefix.m2:1|c\n'] == buf.split_to_packets(prefix='prefix')


def test_buffer_split_to_packets_two_packets_min_size():
    buf = metrics.MetricsBuffer()
    buf.incr('m1', 1)
    buf.incr('m1', 1)
    msg = b'prefix.m1:1|c\n'
    assert [msg] * 2 == buf.split_to_packets(prefix='prefix', packet_size_bytes=len(msg))


async def test_send_empty_metrics_buffer(loop):
    buf = metrics.MetricsBuffer()
    client = metrics.MetricsSender(loop=loop, prefix='')
    assert 0 == await client.send_buffer(buf)


async def test_send_metrics_buffer_with_data(loop):
    buf = metrics.MetricsBuffer()
    buf.incr('m1', 1)
    buf.incr('m1', 1)
    msg = b'm1:1|c\n'
    client = metrics.MetricsSender(loop=loop, prefix='', packet_size_bytes=len(msg))
    assert len(msg) * 2 == await client.send_buffer(buf)


async def test_metrics_info(cli):
    resp = await cli.get('/_info')
    payload = await resp.json()
    assert {'result': 'ok'} == payload
    assert resp.status == 200
