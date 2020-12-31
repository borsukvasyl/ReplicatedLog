import asyncio
import os

from fastapi import APIRouter

from routers.common import MasterStatusModel, GetDataOutModel, AppendDataMasterInModel
from routers.replication import replicate, check_health
from routers.requests import secondary2url

router = APIRouter()
data = []
secondaries = os.environ["SECONDARIES"].split(":")


@router.get("/health", response_model=MasterStatusModel)
async def health():
    statuses = await check_health(secondaries)
    statuses = {node: status for node, status in zip(secondaries, statuses)}
    return MasterStatusModel(statuses=statuses)


@router.get("/get", response_model=GetDataOutModel)
async def get():
    return GetDataOutModel(messages=data)


@router.post("/append")
async def append(message: AppendDataMasterInModel):
    data.append(message.message)

    urls = [f"{secondary2url(hostname)}/append" for hostname in secondaries]
    json = message.dict(exclude={"w"})
    write_concern = message.w - 1

    if write_concern > len(urls):
        raise ValueError(f"Write concern should be lower than the number of nodes [{len(urls) + 1}]")
    await asyncio.ensure_future(replicate(urls, json, write_concern))
