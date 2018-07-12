import sys
import logging
import socket
import json


APP_LOGGER_NAME = 'avio'
DEFAULT_LOGGER_LEVEL = 'INFO'

app_logger = logging.getLogger(APP_LOGGER_NAME)


def configure_app_logger(logger_config: dict = None) -> logging.Logger:
    """
    :param logger_config: {
        'level': 'INFO',
        'use_json_formatter': True,
        'tag': 'avio',
    }
    :return: configured logger
    """

    def _level_by_name(level_name: str) -> int:
        """
        :param level_name:
        :return:
        >>> _level_by_name('DEBUG')
        10
        >>> _level_by_name('info')
        20
        >>> _level_by_name('i')
        20
        """

        if len(level_name) == 1:
            level_map = {
                'd': 'debug',
                'i': 'info',
                'w': 'warning',
                'e': 'error',
                'c': 'critical',
            }
            level_name = level_map.get(level_name.lower(), DEFAULT_LOGGER_LEVEL)

        level_name = level_name.upper()
        return getattr(logging, level_name)

    logger_config = logger_config or {}
    logger_config.setdefault('use_json_formatter', True)
    logger_config.setdefault('tag', 'avio')
    logger_config.setdefault('level', 'warning')

    logger = logging.getLogger(logger_config.get('name', APP_LOGGER_NAME))
    logger.handlers = []
    level = _level_by_name(logger_config['level'])
    logger.setLevel(level)

    if logger_config['use_json_formatter']:
        handler = JsonToStdErrHandler(logger_config['tag'])
        handler.setLevel(level)
        formatter = JsonRecordFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


class JsonRecordFormatter(logging.Formatter):
    """
    A structured formatter.

    Best used with server storing data in an ElasticSearch cluster for example.
    https://github.com/fluent/fluent-logger-python/blob/master/fluent/handler.py

    :param fmt: a dict with format string as values to map to provided keys.
    """
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt=None, datefmt=datefmt)

        self._fmt_dict = fmt or {
            'host': '%(hostname)s',
            'name': '%(name)s',
            'module': '%(module)s',
            'function': '%(funcName)s',
            'lineno': '%(lineno)d',
            'type': '%(type)s',
        }
        self._hostname = socket.gethostname()

    def format(self, record) -> dict:
        super().format(record)
        record.hostname = self._hostname
        record.type = record.levelname[0]

        data = {
            key: value % record.__dict__
            for key, value in self._fmt_dict.items()
        }

        self._structuring(data, record)
        return data

    def _structuring(self, data: dict, record: logging.LogRecord):
        """
        Melds `record.msg` into `data`.

        :param data: dictionary to be sent to server
        :param record: :class:`LogRecord`.
          `record.msg` can be a simple string for backward compatibility with
          :mod:`logging` framework, a JSON encoded string or a dictionary
          that will be merged into dictionary generated in :meth:`format.
        """
        if isinstance(record.msg, dict):
            for key in record.msg:
                if isinstance(record.msg[key], Exception):
                    record.msg[key] = self._get_trace(record, False)
            self._add_dict(data, record.msg)
        elif isinstance(record.msg, str):
            try:
                self._add_dict(data, json.loads(str(record.msg)))
            except ValueError:
                message = record.getMessage()
                if record.exc_text:
                    message += '\n' + record.exc_text
                self._add_dict(data, {'message': message})
        elif isinstance(record.msg, Exception):
            trace = self._get_trace(record)
            self._add_dict(data, {'message': trace})
        else:
            self._add_dict(data, {'message': record.msg})

    def _get_trace(self, record, need_format=True):
        s = ''
        if need_format:
            if hasattr(self, 'formatMessage'):
                s = self.formatMessage(record)
            else:
                s = self._fmt % record.__dict__

        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if hasattr(record, 'stack_info') and record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s

    @staticmethod
    def _add_dict(data, update):
        for key, value in update.items():
            if not isinstance(key, str):
                key = str(key)
            if not isinstance(value, str):
                value = str(value)
            data[key] = value


class JsonToStdErrHandler(logging.Handler):

    def __init__(self, tag: str):
        self.tag = tag
        super().__init__()

    def emit(self, record):
        data = self.format(record)
        data['tag'] = self.tag
        sys.stderr.write(json.dumps(data) + '\n')

    def flush(self):
        self.acquire()
        self.release()

    def close(self):
        self.acquire()
        self.release()
