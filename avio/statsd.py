"""
Possible candidates to replace this method:

cython, have tests, poor pep8
use cystatsd
https://github.com/scivey/aiostatsd
probably dont work https://github.com/scivey/aiostatsd/issues/1

another poor example
https://gist.github.com/baverman/fc0eee788ca204d8e34ee6ff3d0be2e5

not async
https://github.com/qntln/fastatsd
"""


from collections import deque
import socket
import asyncio
from typing import Union
import logging


class StatsdBuffer:
    """
    Protocol description:

    https://github.com/b/statsd_spec
    https://github.com/etsy/statsd/blob/master/docs/metric_types.md
    """
    def __init__(self,
                 prefix='',
                 force_int=True,
                 maxlen=None):

        self._prefix = prefix + '.' if not prefix.endswith('.') else prefix
        self._force_int = force_int
        self._data = deque(maxlen=maxlen)
        self._size = 0

    @property
    def data(self):
        return list(self._data)

    @property
    def to_bytes(self) -> bytes:
        return b''.join(
            entry if isinstance(entry, bytes) else entry.encode('utf8')
            for entry in self._data
        )

    def clear(self):
        self._data = deque()
        self._size = 0

    @property
    def size(self):
        return self._size

    def gauge(self, name, value):
        self._send(name, value, 'g')

    def timing(self, name, value):
        self._send(name, value, 'ms')

    def histogram(self, name, value):
        self._send(name, value, 'h')

    def set(self, name, value):
        self._send(name, value, 's')

    def count(self, name, value):
        self._send(name, value, 'c')

    def incr(self, name, value=1):
        self.count(name, value)

    def decr(self, name, value=1):
        self.count(name, -value)

    def _send(self, name: str, value, _type):
        """
        Generic method to send metric to statsd server.

        :param name: metric name
        :param value: metric value
        :param _type: metric type modifier
        """
        data = self._format(name=name, value=value, _type=_type)
        self._append(data)

    def _format(self, name, value, _type) -> str:
        return '{prefix}{name}:{value}|{_type}\n'.format(
            prefix=self._prefix,
            name=name,
            value=int(value) if self._force_int else value,
            _type=_type
        )

    def _append(self, data):
        self._data.append(data)
        self._size += len(data)

    def __len__(self):
        return self.size

    def __bool__(self):
        return len(self) > 0

    __nonzero__ = __bool__


STATSD_HOST = 'localhost'
STATSD_PORT = 8125


class StatsdClient:
    """
    Protocol description:

    https://github.com/b/statsd_spec
    https://github.com/etsy/statsd/blob/master/docs/metric_types.md
    """

    def __init__(self, host=STATSD_HOST, port=STATSD_PORT, loop=None, logger=None):
        self._loop = loop or asyncio.get_event_loop()
        self._addr = (host, port)
        self._udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_sock.setblocking(False)
        self._logger = logger or logging.getLogger('statsd')

    def close(self):
        self._udp_sock.close()

    async def send_buffer(self, buffer: StatsdBuffer):
        try:
            await sendto(self._loop, self._udp_sock, buffer.to_bytes, self._addr)
        except:
            log.exception('cant send data')
        buffer.clear()


def sendto(loop, sock, data, addr, fut=None, registed=False):
    """
    # https://www.pythonsheets.com/notes/python-asyncio.html
    :return: Future, resulting in number of bytes sent.
    """
    fd = sock.fileno()
    if fut is None:
        fut = loop.create_future()
    if registed:
        loop.remove_writer(fd)
    try:
        n = sock.sendto(data, addr)
    except (BlockingIOError, InterruptedError):
        loop.add_writer(fd, sendto, loop, sock, data, addr, fut, True)
    else:
        fut.set_result(n)
    return fut
