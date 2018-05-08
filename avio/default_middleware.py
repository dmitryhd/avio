"""
Doc on middlewares
https://docs.aiohttp.org/en/stable/web_advanced.html#middlewares
"""
import time
import traceback

from aiohttp import web

from avio.api_handler import ApiHandler
from avio import log as log

UNHANDLED_ERROR_MESSAGE = 'Wild error occured!'


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
    # TODO: mb handle ensure json
    # TODO: here might go fire and forget coroutines, like sending stats and exceptions
    # https://stackoverflow.com/questions/37278647/fire-and-forget-python-async-await
    return web.json_response(response, status=status)


@web.middleware
async def measure_time(request, handler):
    """
    Internally, a single request handler is constructed by applying the middleware chain to the original handler
    in reverse order, and is called by the RequestHandler as a regular handler.

    So, this middleware should be called first and specified last!
    """

    if issubclass(handler, ApiHandler):  # Note: only api calls can measure time
        handler_instance = handler(request)
        start = time.time()
        try:
            with handler_instance.timeit('response'):
                return await handler_instance
        finally:
            end = time.time()
            elapsed = end - start
            handler_instance.timers["response"] = elapsed
            log.app_logger.info(f'response took {handler_instance.timers["response"]:.3f} s')
    else:
        response = await handler(request)

    return response
