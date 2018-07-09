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

# TODO: work in proggress now

from collections import deque
import logging
import socket

__all__ = ['Buffer']


class Buffer:
    def __init__(self):
        self._data = deque()
        self._size = 0

    @property
    def data(self):
        return self._data

    @property
    def size(self):
        return self._size

    def __len__(self):
        return self.size

    def to_bytes(self):
        return b''.join(self.data)

    def __bool__(self):
        return len(self) > 0

    __nonzero__ = __bool__

    def append(self, data):
        self._data.append(data)
        self._size += len(data)

    def clear(self):
        self._data = deque()
        self._size = 0


log = logging.getLogger(__name__)


# This is most likely for Intranets.
FAST_ETHERNET_MTU = 1432
# Jumbo frames can make use of this feature much more efficient.
GIGABIT_ETHERNET_MTU = 8932
# Commodity Internet
COMMODITY_INTERNET_MTU = 512


class Transport:
    def __init__(self,
                 io_loop,
                 host,
                 port,
                 enable=True,
                 protocol='udp',
                 auto_flush=False,
                 max_buffer_size=None,
                 ipv6=False):
        self.io_loop = io_loop
        self.host = host
        self.port = port
        self.enable = enable
        self.protocol = protocol.lower()
        self.max_buffer_size = max_buffer_size
        self.auto_flush = auto_flush
        self.ipv6 = ipv6

        self.stream = None
        self.buffer = Buffer()

        self._closed = False

    def closed(self):
        return self._closed

    async def write(self, data):
        log.debug('Append data to buffer.')

        if isinstance(data, str):
            data = data.encode('utf-8')

        if self.max_buffer_size is not None and \
           len(self.buffer) + len(data) >= self.max_buffer_size:
            log.debug('Flush buffer before append new data to prevent overflow.')
            await self.flush()

        self.buffer.append(data)

        if self.auto_flush:
            log.debug('Try to call flush by auto_flush.')
            await self.flush()

    async def flush(self):
        if self._closed:
            raise RuntimeError("flush() called on closed transport instance")

        log.debug('Flush the buffer.')

        if not self.buffer:
            log.debug('Buffer is empty.')
            return

        try:
            if self.enable:
                await self.connect()

                log.debug('Write the buffer to stream.')

                await self.stream.write(self.buffer.to_bytes())
        except StreamBufferFullError as exc:
            log.exception(exc)

            log.warning(
                'Clear the buffer on overflow max size={}.'.format(self.max_buffer_size)
            )
            self.buffer.clear()

        except StreamClosedError as exc:
            log.exception(exc)
            log.warning('Stream closed. Unable to write the buffer.')

        except socket.error as exc:
            log.exception(exc)
            log.warning(
                'Connection error "{exc}". Unable to write the buffer.'.format(exc=exc))
        else:
            log.debug('Clear the buffer.')

            self.buffer.clear()

    async def connect(self):
        if self.max_buffer_size is not None and len(self.buffer) >= self.max_buffer_size:
            raise StreamBufferFullError('Reached maximum write buffer size')

        if not self.stream or self.stream.closed():
            self.stream = self.create_stream()

            await self.stream.connect((self.host, self.port))

    async def close(self):
        log.debug('Close the transport.')

        async self.flush()

        if self.stream:
            log.debug('Close the stream.')

            self.stream.close()
            self.stream = None

        self._closed = True

    def create_stream(self):
        log.debug('Create stream with max_buffer_size={}.'.format(self.max_buffer_size))

        sock = self.create_socket()

        # TODO
        return IOStream(
            sock,
            io_loop=self.io_loop,
            max_write_buffer_size=self.max_buffer_size
        )

    # TODO
    def create_socket(self):
        log.debug('Create {protocol} socket: {host}:{port}.'.format(
            protocol=self.protocol, host=self.host, port=self.port
        ))

        family = socket.AF_INET6 if self.ipv6 else socket.AF_INET

        if self.protocol == 'udp':
            return socket.socket(family, socket.SOCK_DGRAM)

        return socket.socket(family, socket.SOCK_STREAM)



STATSD_HOST = 'localhost'
STATSD_PORT = 8125


class Statsd:
    """
    Statsd client.

    Protocol description:

    https://github.com/b/statsd_spec
    https://github.com/etsy/statsd/blob/master/docs/metric_types.md
    """
    def __init__(self,
                 io_loop=None,
                 host=STATSD_HOST,
                 port=STATSD_PORT,
                 enable=True,
                 prefix='',
                 protocol='udp',
                 auto_flush=False,
                 max_buffer_size=COMMODITY_INTERNET_MTU,
                 ipv6=False,
                 force_int=True):
        self.prefix = prefix + '.' if not prefix.endswith('.') else prefix
        self.force_int = force_int

        self._transport = Transport(
            io_loop=io_loop,
            host=host,
            port=port,
            enable=enable,
            protocol=protocol,
            auto_flush=auto_flush,
            max_buffer_size=max_buffer_size,
            ipv6=ipv6
        )

    def closed(self):
        return self._transport.closed()

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

    async def send(self, name, value, _type):
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