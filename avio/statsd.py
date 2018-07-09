"""
cython, have tests, poor pep8
use cystatsd
https://github.com/scivey/aiostatsd
probably dont work https://github.com/scivey/aiostatsd/issues/1

another poor example
https://gist.github.com/baverman/fc0eee788ca204d8e34ee6ff3d0be2e5

not async
https://github.com/qntln/fastatsd

???
https://pypi.python.org/pypi/aiomeasures/0.5.14


https://docs.atlassian.com/aiostats/latest/index.html
"""


from collections import deque
import socket
import asyncio
from typing import Union


# This is most likely for Intranets.
FAST_ETHERNET_MTU = 1432
# Jumbo frames can make use of this feature much more efficient.
GIGABIT_ETHERNET_MTU = 8932
# Commodity Internet
COMMODITY_INTERNET_MTU = 512

STATSD_HOST = 'localhost'
STATSD_PORT = 8125


class UDPClient:

    def __init__(self, host, port, loop=None):
        self._loop = asyncio.get_event_loop() if loop is None else loop
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setblocking(False)
        self._addr = (host, port)
        self._future = None
        self._data = None

    def sendto(self, data: Union[bytes, str]):
        self._future = asyncio.Future(loop=self._loop)
        self.data = data if isinstance(data, bytes) else str(data).encode('utf-8')
        self._loop.add_writer(self._sock.fileno(), self._try_to_send)
        return self._future

    def _try_to_send(self):
        try:
            self._sock.sendto(self.data, self._addr)
        except (BlockingIOError, InterruptedError):
            return
        except Exception as exc:
            self.abort(exc)
        else:
            self.close()
            self._future.set_result(True)

    def abort(self, exc):
        self.close()
        self._future.set_exception(exc)

    def close(self):
        self._loop.remove_writer(self._sock.fileno())
        self._sock.close()


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
        return self._data

    @property
    def size(self):
        return self._size

    def count(self, name, value):
        self.send(name, value, 'c')

    def incr(self, name, value=1):
        self.count(name, value)

    def decr(self, name, value=1):
        self.count(name, -value)

    def gauge(self, name, value):
        self.send(name, value, 'g')

    def timing(self, name, value):
        self.send(name, value, 'ms')

    def histogram(self, name, value):
        self.send(name, value, 'h')

    def set(self, name, value):
        self.send(name, value, 's')

    def send(self, name: str, value, _type):
        """
        Generic method to send metric to statsd server.

        :param name: metric name
        :param value: metric value
        :param _type: metric type modifier
        """
        data = self.format(name=name, value=value, _type=_type)
        self._append(data)

    def format(self, name, value, _type) -> str:
        return '{prefix}{name}:{value}|{_type}\n'.format(
            prefix=self._prefix,
            name=name,
            value=int(value) if self._force_int else value,
            _type=_type
        )

    def _append(self, data):
        self._data.append(data)
        self._size += len(data)

    def _clear(self):
        self._data = deque()
        self._size = 0

    def __len__(self):
        return self.size

    def __bool__(self):
        return len(self) > 0

    __nonzero__ = __bool__



class StatsdClient:
    """
    Protocol description:

    https://github.com/b/statsd_spec
    https://github.com/etsy/statsd/blob/master/docs/metric_types.md
    """
    def __init__(self,
                 host=STATSD_HOST,
                 port=STATSD_PORT,
                 enabled=True,
                 prefix='',
                 ipv6=False,
                 force_int=True,
                 loop=None):
        self._enabled = enabled
        self._prefix = prefix + '.' if not prefix.endswith('.') else prefix
        self._force_int = force_int
        if self._enabled:
            self._upd_client = UDPClient(host, port, loop=loop)

    async def count(self, name, value):
        await self.send(name, value, 'c')

    async def incr(self, name, value=1):
        await self.count(name, value)

    async def decr(self, name, value=1):
        await self.count(name, -value)

    async def gauge(self, name, value):
        await self.send(name, value, 'g')

    async def timing(self, name, value):
        await self.send(name, value, 'ms')

    async def histogram(self, name, value):
        await self.send(name, value, 'h')

    async def set(self, name, value):
        await self.send(name, value, 's')

    async def send(self, name: str, value, _type):
        """
        Generic method to send metric to statsd server.

        :param name: metric name
        :param value: metric value
        :param _type: metric type modifier
        """
        data = self.format(name=name, value=value, _type=_type)

        await self._transport.write(data)

    def format(self, name, value, _type):
        return '{prefix}{name}:{value}|{_type}\n'.format(
            prefix=self.prefix,
            name=name,
            value=int(value) if self.force_int else value,
            _type=_type
        )

    async def flush(self):
        await self._transport.flush()

    async def close(self):
        await self._transport.close()