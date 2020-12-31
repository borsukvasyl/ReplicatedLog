import os

from fastapi import APIRouter

from routers.common import MasterStatusModel, GetDataOutModel, MasterAppendDataModel
from routers.replication import check_health, Replicator

router = APIRouter()
secondaries = os.environ["SECONDARIES"].split(":")
replicator = Replicator(secondaries)


@router.get("/health", response_model=MasterStatusModel)
async def health():
    statuses = await check_health(secondaries)
    statuses = {node: status for node, status in zip(secondaries, statuses)}
    return MasterStatusModel(statuses=statuses)


@router.get("/get", response_model=GetDataOutModel)
async def get():
    return GetDataOutModel(messages=replicator.messages)


@router.post("/append")
async def append(message: MasterAppendDataModel):
    if message.w < 1 or message.w > len(secondaries) + 1:
        raise ValueError(f"Write concern should be in range [1, {len(secondaries) + 1}]")
    future = replicator.replicate(message.message, message.w)
    await future
