import asyncio

import aiohttp


def secondary2url(hostname: str):
    return f"http://{hostname}:8000"


async def gather_get(urls: [str]):
    async with aiohttp.ClientSession() as session:
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(async_get(url, session)) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        statuses = [None if isinstance(response, BaseException) else response for response in responses]
        return statuses


async def async_post(url: str, json: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json) as response:
            return response


async def async_get(url: str, session: aiohttp.ClientSession):
    async with session.get(url) as response:
        return await response.json()
