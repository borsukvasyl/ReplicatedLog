import asyncio
import os
from typing import List

import aiohttp
from fastapi import APIRouter, status

from routers.common import StatusModel, GetDataOutModel, AppendDataMasterInModel

router = APIRouter()
data = []
secondaries = [f"http://{hostname}:8000" for hostname in os.environ["SECONDARIES"].split(":")]


@router.get("/health", response_model=StatusModel)
async def health():
    return StatusModel(status="OK")


@router.get("/get", response_model=GetDataOutModel)
async def get():
    return GetDataOutModel(messages=data)


@router.post("/append")
async def append(message: AppendDataMasterInModel):
    data.append(message.message)

    urls = [f"{hostname}/append" for hostname in secondaries]
    json = message.dict(exclude={"w"})
    write_concern = message.w - 1

    if write_concern > len(urls):
        raise ValueError(f"Write concern should be lower than the number of nodes [{len(urls) + 1}]")
    await asyncio.ensure_future(replicate(urls, json, write_concern))


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
        task = asyncio.ensure_future(post_secondary(url, json))
        task.add_done_callback(_done_callback)

    if write_concern == 0:
        future.set_result(True)

    return await future


async def post_secondary(url: str, json: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json) as response:
            return response
