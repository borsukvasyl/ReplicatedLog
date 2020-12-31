import asyncio
import os

from fastapi import APIRouter

from routers.common import MasterStatusModel, GetDataOutModel, AppendDataMasterInModel
from routers.replication import replicate, check_health

router = APIRouter()
data = []
secondaries = os.environ["SECONDARIES"].split(":")
secondary_urls = [f"http://{hostname}:8000" for hostname in secondaries]


@router.get("/health", response_model=MasterStatusModel)
async def health():
    urls = [f"{secondary}/health" for secondary in secondary_urls]
    statuses = await check_health(urls)
    statuses = {node: status for node, status in zip(secondaries, statuses)}
    return MasterStatusModel(statuses=statuses)


@router.get("/get", response_model=GetDataOutModel)
async def get():
    return GetDataOutModel(messages=data)


@router.post("/append")
async def append(message: AppendDataMasterInModel):
    data.append(message.message)

    urls = [f"{hostname}/append" for hostname in secondary_urls]
    json = message.dict(exclude={"w"})
    write_concern = message.w - 1

    if write_concern > len(urls):
        raise ValueError(f"Write concern should be lower than the number of nodes [{len(urls) + 1}]")
    await asyncio.ensure_future(replicate(urls, json, write_concern))
