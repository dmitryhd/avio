import logging
from functools import partial

from aiohttp import web
from raven import Client
from raven_aiohttp import QueuedAioHttpTransport, AioHttpTransport
from raven.handlers.logging import SentryHandler

from avio.log import get_log_level_by_name, APP_LOGGER_NAME


async def configure_sentry(app: web.Application):
    """
    Note: this function must be coroutine!
    """

    logger_config = app['config'].get('logging', {})

    if not logger_config.get('sentry_enabled'):
        return

    dsn = logger_config.get('sentry_dsn')
    if not dsn:
        raise ValueError('Sentry dsn should be set.')

    sentry_client = Client(
        dsn=dsn,
        raise_send_errors=False,
        concurrent=logger_config.get('sentry_concurrent', 2),
        transport=_get_sentry_transport(logger_config),
        enable_breadcrumbs=logger_config.get('sentry_enable_breadcrumbs', False),
    )
    app['sentry_client'] = sentry_client

    sentry_handler = SentryHandler(sentry_client)
    sentry_level = get_log_level_by_name(logger_config.get('sentry_level', 'WARN'))
    sentry_handler.setLevel(sentry_level)
    sentry_formatter = SentryFormatter()
    sentry_handler.setFormatter(sentry_formatter)

    logger = logging.getLogger(logger_config.get('name', APP_LOGGER_NAME))
    logger.addHandler(sentry_handler)


async def dispose_sentry(app: web.Application):
    if 'sentry_client' in app:
        await app['sentry_client'].remote.get_transport().close()


class SentryFormatter(logging.Formatter):

    def format(self, record):
        if isinstance(record.msg, dict) and 'message' in record.msg:
            record.data = {k: v for k, v in record.msg.items() if k != 'message'}
            record.msg = record.msg['message']
        return super().format(record)


def _get_sentry_transport(logger_config: dict):
    transport_type = logger_config.get('sentry_transport', 'queued')
    if transport_type == 'queued':
        num_workers = logger_config.get('sentry_transport_workers', 2)
        queue_size = logger_config.get('sentry_transport_queue_size', 500)

        transport = partial(
            QueuedAioHttpTransport,
            workers=num_workers,
            qsize=queue_size,
        )
    else:
        transport = AioHttpTransport

    return transport
