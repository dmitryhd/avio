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

# TODO: document middlewares


@web.middleware
async def format_exceptions(request, handler):
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
    except web.HTTPException as ex:
        status = ex.status
        traceback_str = traceback.format_exc()
        message = ex.reason

    except Exception:
        status = 500
        traceback_str = traceback.format_exc()
        message = UNHANDLED_ERROR_MESSAGE

    response = {
        'code': status,
        'message': message,
        'traceback': traceback_str,  # TODO: make traceback optional
    }
    log.app_logger.info(traceback_str)
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

        for timer_name, seconds in request.timers.items():
            request.metrics_buffer.timing(timer_name, seconds * 1000)  # NOTE: conversion to ms.

        # TODO: here might go fire and forget coroutines, like sending stats and exceptions
        # https://stackoverflow.com/questions/37278647/fire-and-forget-python-async-await
        await request.app['metrics_sender'].send_buffer(request.metrics_buffer)

        # TODO: remove later
        num_tasks = len(asyncio.Task.all_tasks())
        log.app_logger.info(f'response took {request.timers["response"]:.3f} s, {num_tasks:,} running')
