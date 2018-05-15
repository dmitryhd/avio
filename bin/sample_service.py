#!/usr/bin/env python3

import os.path as path
import sys
import asyncio
import time

cur_dir = path.dirname(path.abspath(__file__))
sys.path.append(path.join(cur_dir, '..'))

from avio.api_handler import ApiHandler
from avio.application import make_app, run_app
from avio.json_api_client import JsonApiClient


class SampleHandler(ApiHandler):

    async def get(self):
        btime = time.time()
        cli = self.app['client']
        res = await cli.get('')
        print(cli)
        futures = [cli.get(''), cli.get(''), cli.get('')]
        results = await asyncio.gather(*futures)
        print(results)
        elapsed = time.time() - btime
        t1 = round(res.seconds_run, 4)
        t2 = round(results[0].seconds_run, 4)
        t3 = round(results[1].seconds_run, 4)
        t4 = round(results[2].seconds_run, 4)

        return self.finalize({
            '1 coroutine': t1,
            '2 coroutine': t2,
            '3 coroutine': t3,
            '4 coroutine': t4,
            'total time ': round(elapsed, 4),
            'diff': t1 + t2 + t3 + t4 - elapsed,
        })


def main():
    app = make_app()

    client = JsonApiClient('http://localhost:8888', timeout_seconds=0.4)
    app['client'] = client

    app.router.add_view('/sample', SampleHandler)

    run_app(app)


if __name__ == '__main__':
    main()
