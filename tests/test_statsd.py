from avio import statsd
from collections import deque


def test_format_metric():
    buf = statsd.StatsdBuffer(prefix='prefix')
    assert deque([]) == buf.data
    buf.incr('m1', 2)
    assert deque(['prefix.m1:2|c\n']) == buf.data
    buf.incr('m1', 2)
    assert deque(['prefix.m1:2|c\n']) == buf.data

