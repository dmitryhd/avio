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

    status = 200
    message = ''
    traceback_str = ''
    try:
        # If no exception raised - return response straight away
        return await handler(request)
        # Note: i can access view class instance by handler.__self__

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

    handler_instance = handler.__self__

    if issubclass(handler, ApiHandler):
    # Note: only api calls can mea
        with handler_instance.timeit('response'):
            response = await handler(request)
        log.app_logger.info(f'Response took {handler_instance.timer["response"]:.3f} s')
    else:
        response = await handler(request)

    return response
