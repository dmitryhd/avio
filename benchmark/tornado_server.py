#!/usr/bin/env python3
import tornado.ioloop
import tornado.web
import tornado.gen
from tornado.ioloop import IOLoop


class MainHandler(tornado.web.RequestHandler):

    async def get(self):
        await tornado.gen.sleep(0.05)
        self.write('')


def make_app(uvloop=False):
    if uvloop:
        IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
        import asyncio
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    return tornado.web.Application([(r'/sleep50', MainHandler)])



if __name__ == "__main__":
    app = make_app(uvloop=True)
    app.listen(8890)
    tornado.ioloop.IOLoop.current().start()
