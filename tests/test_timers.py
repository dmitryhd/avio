import time
import asyncio
from avio.api_handler import ApiHandler


async def test_timeit_async():
    handler = ApiHandler(None)
    sleep_time = 0.01
    with handler.timeit('time1'):
        await asyncio.sleep(0.01)
    assert sleep_time == round(handler.timers['time1'], 2)


async def test_timeit_sync():
    handler = ApiHandler(None)
    sleep_time = 0.01
    precision = 2
    with handler.timeit('time1'):
        time.sleep(sleep_time)
    with handler.timeit('time2'):
        time.sleep(sleep_time)
    assert round(sleep_time, precision) == round(handler.timers['time1'], precision)
    assert round(sleep_time, precision) == round(handler.timers['time2'], precision)
