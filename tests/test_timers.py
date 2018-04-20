import time
import asyncio
from avio.api_handler import ApiHandler


async def test_timeit_async():
    handler = ApiHandler(None)
    sleep_time = 0.05
    with handler.timeit('time1'):
        await asyncio.sleep(0.05)
    assert sleep_time == handler.timers['time1']


async def test_timeit_sync():
    handler = ApiHandler(None)
    sleep_time = 0.05
    with handler.timeit('time1'):
        time.sleep(sleep_time)
    with handler.timeit('time2'):
        time.sleep(sleep_time)
    assert sleep_time == handler.timers['time1']
    assert sleep_time == handler.timers['time2']
