import sys
import logging


APP_LOGGER_NAME = 'avio'


def _level_by_name(level_name) -> int:
    """
    :param level_name:
    :return:
    >>> _level_by_name('DEBUG')
    10
    >>> _level_by_name('info')
    20
    """
    level_name = level_name.upper()
    return getattr(logging, level_name)


def configure_app_logger(logger_config: dict = None) -> logging.Logger:
    """
    :param logger_config:
    :return:
    """
    logger_config = logger_config or {}
    logger = logging.getLogger(logger_config.get('name', APP_LOGGER_NAME))
    logger.handlers = []
    level = _level_by_name(logger_config.get('level', 'info'))
    logger.setLevel(level)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


app_logger = logging.getLogger(APP_LOGGER_NAME)
