import time
import datetime

from avio.api_handler import ApiHandler


class InfoHandler(ApiHandler):

    async def get(self):
        info = {'result': 'ok'}
        return self.finalize(info)


class ErrorHandler(ApiHandler):

    async def get(self):
        raise Exception('Somebody activated _error handler')


class EchoHandler(ApiHandler):

    async def post(self):
        j = await self.request_json()
        return self.finalize(j)


class DetailedInfoHandler(ApiHandler):

    async def get(self):

        age_seconds = round(time.time() - self.app['start_ts'], 2)
        sec = datetime.timedelta(seconds=age_seconds)
        age = datetime.datetime(1, 1, 1) + sec

        age_human = f'{age.day - 1} days {age.hour} hours {age.minute} minutes {age.second} seconds'
        info = {
            'appRunning': age_human,
            'ageSeconds': age_seconds,
        }
        return self.finalize(info)
