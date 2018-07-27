"""
Doc on middlewares
https://docs.aiohttp.org/en/stable/web_advanced.html#middlewares
"""
import time
import traceback

from aiohttp import web
import asyncio

from avio import log as log
from avio.metrics import MetricsBuffer


UNHANDLED_ERROR_MESSAGE = 'Wild error occured!'


@web.middleware
async def format_exceptions(request: web.Request, handler):
    """
    Middleware, that leaves responses, that don't raise exceptions unchanged.

    Converts all errors to common format, containing
    - http error code
    - human readable message
    - traceback

    NOTE: on json handling https://aiohttp.readthedocs.io/en/stable/web_advanced.html#example
    """

    try:
        # If no exception raised - return response straight away
        return await handler(request)

    # Jsonify any http exception on wrong url
    except web.HTTPError as ex:
        log.app_logger.exception('')
        status = ex.status
        traceback_str = traceback.format_exc()
        message = ex.reason

    except Exception:
        log.app_logger.exception('')
        status = 500
        traceback_str = traceback.format_exc()
        message = UNHANDLED_ERROR_MESSAGE

    response = {
        'code': status,
        'message': message,
        'traceback': traceback_str,  # TODO: make traceback optional
    }
    return web.json_response(response, status=status)


@web.middleware
async def measure_time_and_send_metrics(request, handler):
    """
    Internally, a single request handler is constructed by applying the middleware chain to the original handler
    in reverse order, and is called by the RequestHandler as a regular handler.

    So, this middleware should be called first and specified last!
    """

    request.timers = {}
    request.metrics_buffer = MetricsBuffer()
    start = time.time()
    try:
        return await handler(request)
    finally:
        end = time.time()
        elapsed = end - start
        request.timers['response'] = elapsed

        if 'metrics_sender' in request.app:

            for timer_name, seconds in request.timers.items():
                request.metrics_buffer.timing_sec(timer_name, seconds)

            # Fire and forget metric
            asyncio.ensure_future(request.app['metrics_sender'].send_buffer(request.metrics_buffer))

        # Debug output
        # num_tasks = len(asyncio.Task.all_tasks())
        # msg = f'response took {request.timers["response"]:.3f} s, {num_tasks:,} coroutines running'
        # log.access_logger.debug(msg)
