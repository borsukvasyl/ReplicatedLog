import asyncio
from typing import List

from fastapi import status

from routers.common import NodeStatus
from routers.requests import async_post, gather_get


async def replicate(urls: List[str], json: dict, write_concern: int):
    future = asyncio.Future()
    n_success, n_finished = 0, 0

    def _done_callback(fut: asyncio.Future):
        nonlocal n_success, n_finished
        n_finished += 1
        if fut.exception() is None and fut.result().status == status.HTTP_200_OK:
            n_success += 1

        if n_success == write_concern:
            future.set_result(True)
        elif n_finished == len(urls) and n_success < write_concern:
            future.set_exception(RuntimeError(f"Failed to replicate on {write_concern} nodes"))

    for url in urls:
        task = asyncio.ensure_future(async_post(url, json))
        task.add_done_callback(_done_callback)

    if write_concern == 0:
        future.set_result(True)

    return await future


async def check_health(urls: List[str]):
    responses = await gather_get(urls)
    statuses = [NodeStatus.unhealthy if response is None else NodeStatus(response["status"]) for response in responses]
    return statuses
