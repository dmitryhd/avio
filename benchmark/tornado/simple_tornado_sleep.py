#!/usr/bin/env python3
import tornado.ioloop
import tornado.web
import tornado.gen
import json
import time

class MainHandler(tornado.web.RequestHandler):

    async def get(self):
        b = time.time()
        await tornado.gen.sleep(0.05)
        e = time.time()
        print(e - b)
        self.write(json.dumps({}))

def make_app():
    return tornado.web.Application([
        (r"/sleep50", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8890)
    tornado.ioloop.IOLoop.current().start()