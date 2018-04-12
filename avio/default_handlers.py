from aiohttp import web


class InfoHandler(web.View):

    async def get(self):
        info = {'result': 'ok'}
        return web.json_response(info)


class ErrorHandler(web.View):

    async def get(self):
        raise Exception('Somebody activated _error handler')
