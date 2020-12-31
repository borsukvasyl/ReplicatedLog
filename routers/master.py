import os

from fastapi import APIRouter

from routers.common import MasterStatusModel, GetDataOutModel, MasterAppendDataModel, NodeStatus
from routers.replication import Replicator

router = APIRouter()
secondaries = os.environ["SECONDARIES"].split(":")
replicator = Replicator(secondaries)
quorum = 1


@router.get("/health", response_model=MasterStatusModel)
async def health():
    return MasterStatusModel(statuses=replicator.healths)


@router.get("/get", response_model=GetDataOutModel)
async def get():
    return GetDataOutModel(messages=replicator.messages)


@router.post("/append")
async def append(message: MasterAppendDataModel):
    healths = list(replicator.healths.values())
    num_healthy = healths.count(NodeStatus.healthy)
    if num_healthy < quorum:
        raise ValueError(f"Number of healthy nodes [{num_healthy}] is lower than quorum [{quorum}]")

    if message.w < 1 or message.w > len(secondaries) + 1:
        raise ValueError(f"Write concern should be in range [1, {len(secondaries) + 1}]")
    future = replicator.replicate(message.message, message.w)
    await future
