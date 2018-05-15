#!/usr/bin/env python3

import os.path as path
import sys

cur_dir = path.dirname(path.abspath(__file__))
sys.path.append(path.join(cur_dir, '..'))

from avio.api_handler import ApiHandler
from avio.application import make_app, run_app
from avio.json_api_client import JsonApiClient


class SampleHandler(ApiHandler):

    async def get(self):
        cli = self.app['google_client']
        res = await cli.get('')
        print(res)
        return self.finalize({'sdfvsd': 'sdf'})


def main():
    app = make_app()

    google_client = JsonApiClient('http://google.com', timeout_seconds=0.4)
    app['google_client'] = google_client

    app.router.add_view('/sample', SampleHandler)

    run_app(app)


if __name__ == '__main__':
    main()
