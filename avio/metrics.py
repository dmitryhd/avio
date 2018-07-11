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

__all__ = (
    'MetricsBuffer',
    'MetricsSender',
    'DummyMetricsSender',
    'FAST_ETHERNET_MTU',
    'GIGABIT_ETHERNET_MTU',
    'COMMODITY_INTERNET_MTU',
    'STATSD_PORT',
    'STATSD_HOST',
)


from collections import deque
from typing import List, Union
import socket
import asyncio
import logging

# This is most likely for Intranets.
FAST_ETHERNET_MTU = 1432
# Jumbo frames can make use of this feature much more efficient.
GIGABIT_ETHERNET_MTU = 8932
# Commodity Internet
COMMODITY_INTERNET_MTU = 512

MAX_MESSAGES_IN_BUFFER = 1000


class MetricsBuffer:

    def __init__(self, force_int=True, max_messages=MAX_MESSAGES_IN_BUFFER):
        self._force_int = force_int
        self._data = deque(maxlen=max_messages)
        self._size = 0

    @property
    def data(self) -> List[bytes]:
        return list(self._data)

    @property
    def size(self):
        return self._size

    def clear(self):
        self._data = deque()
        self._size = 0

    def extend(self, buffer):
        """
        Adds another buffer to current buffer at the end of queue.
        """
        self._data.extend(buffer._data)
        self._size += sum((len(entry) for entry in buffer._data))

    def gauge(self, name, value):
        self._set_metric(name, value, b'g')

    def timing(self, name, value):
        self._set_metric(name, value, b'ms')

    def histogram(self, name, value):
        self._set_metric(name, value, b'h')

    def set(self, name, value):
        self._set_metric(name, value, b's')

    def count(self, name, value):
        self._set_metric(name, value, b'c')

    def incr(self, name, value=1):
        self.count(name, value)

    def decr(self, name, value=1):
        self.count(name, -value)

    def split_to_packets(self,
                         prefix: Union[str, bytes] = '',
                         packet_size_bytes: int = FAST_ETHERNET_MTU) -> List[bytes]:
        """
        :param prefix: statsd prefix. Example: 'service.rec.app.01'
        :param packet_size_bytes: maximum size of packet to avoid fragmentation
        :return: list of bytes, each element == payload of upd packet, ready to be sent
        """
        if isinstance(prefix, str):
            if prefix.endswith('.'):
                prefix = prefix[:-1]
            if prefix:
                prefix = prefix + '.'
            prefix = prefix.encode('utf8')

        prefix_len = len(prefix)

        packets = []
        current_packet_entries = []
        current_packet_size = 0
        for entry in self._data:

            # Start filling new packet
            if current_packet_size + len(entry) + prefix_len > packet_size_bytes:
                packets.append(b''.join(current_packet_entries))
                current_packet_entries.clear()
                current_packet_size = 0

            formatted_entry = prefix + entry
            current_packet_entries.append(formatted_entry)
            current_packet_size += len(formatted_entry)

        # last packet
        if current_packet_size:
            packets.append(b''.join(current_packet_entries))
            current_packet_entries.clear()

        return packets

    def _format(self, name: Union[str, bytes], value: Union[int, float], _type: Union[str, bytes]) -> bytes:
        name = name if isinstance(name, bytes) else name.encode('utf8')
        _type = _type if isinstance(_type, bytes) else _type.encode('utf8')
        return b'%s:%d|%s\n' % (
            name,
            int(value) if self._force_int else value,
            _type,
        )

    def _set_metric(self, name: Union[str, bytes], value: Union[int, float], _type: Union[str, bytes]):
        data = self._format(name=name, value=value, _type=_type)
        self._data.append(data)
        self._size += len(data)

    def __len__(self):
        return self.size

    def __bool__(self):
        return len(self) > 0

    __nonzero__ = __bool__


STATSD_HOST = 'localhost'
STATSD_PORT = 8125


class MetricsSender:
    """
    Protocol description:

    https://github.com/b/statsd_spec
    https://github.com/etsy/statsd/blob/master/docs/metric_types.md
    """

    def __init__(self,
                 host=STATSD_HOST,
                 port=STATSD_PORT,
                 prefix='',
                 loop=None,
                 logger=None,
                 packet_size_bytes: int = FAST_ETHERNET_MTU):

        self._prefix = prefix
        self._packet_size_bytes = packet_size_bytes
        self._addr = (host, port)
        self._loop = loop or asyncio.get_event_loop()

        if logger:
            self._logger = logger
        else:
            logger = logging.getLogger('statsd')
            logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            logger.addHandler(ch)
            self._logger = logger

        self._udp_sock = None
        self._create_socket()

    def close(self):
        self._udp_sock.close()

    async def send_buffer(self, buffer: MetricsBuffer) -> int:
        """
        Note: during send buffer you can always safely add new metrics to this buffer.
        :return: number of bytes sent
        """
        try:

            # Strip information to be sent from this buffer
            packets_to_send = buffer.split_to_packets(self._prefix, packet_size_bytes=self._packet_size_bytes)
            if not len(packets_to_send):
                return 0
            buffer.clear()

            # Start sending packets, now anything new can be added to this buffer
            bytes_sent = 0
            for packet in packets_to_send:
                bytes_sent += await self._send_to(self._loop, self._udp_sock, packet, self._addr)
            return bytes_sent
        except:  # noqa
            self._logger.exception('Cant send statsd data')
            return 0

    def _send_to(self, loop, sock, data, addr, fut=None, registed=False):
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
            loop.add_writer(fd, self._send_to, loop, sock, data, addr, fut, True)
        else:
            fut.set_result(n)
        return fut

    def _create_socket(self):
        self._udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_sock.setblocking(False)


class DummyMetricsSender(MetricsSender):
    """
    Simple metrics sender for testing purposes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = []

    def close(self):
        pass

    def _create_socket(self):
        pass

    def _send_to(self, loop, sock, data, addr, fut=None, registed=False):
        future = loop.create_future()
        future.set_result(0)
        self.metrics.append(data)
        return future
