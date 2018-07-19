#!/usr/bin/env python3

import asyncio
from aiohttp import web
import uvloop


async def sleep50(_):
    await asyncio.sleep(0.05)
    return web.Response(text="")


def init():
    app = web.Application()
    app.router.add_get('/sleep50', sleep50)
    return app


web.run_app(init(), port=8890)