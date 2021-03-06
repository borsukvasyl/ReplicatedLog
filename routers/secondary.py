import os
import asyncio

from fastapi import APIRouter

from routers.common import NodeStatus, SecondaryStatusModel, GetDataOutModel, SecondaryAppendDataModel

router = APIRouter()
data = []
sleep = int(os.environ.get("SLEEP", 0))
suspended = False


@router.get("/health", response_model=SecondaryStatusModel)
async def health():
    status = NodeStatus.suspended if suspended else NodeStatus.healthy
    return SecondaryStatusModel(status=status)


@router.get("/suspend")
async def suspend():
    global suspended
    suspended = True


@router.get("/unsuspend")
async def unsuspend():
    global suspended
    suspended = False


@router.get("/get", response_model=GetDataOutModel)
async def get():
    if suspended:
        raise ValueError("Node is suspended")
    return GetDataOutModel(messages=data)


@router.post("/append")
async def append(message: SecondaryAppendDataModel):
    if suspended:
        raise ValueError("Node is suspended")
    if message.message_id > len(data):
        raise ValueError(f"Message id [{message.message_id}] is larger than current acceptable id [{len(data)}]")

    await asyncio.sleep(sleep)
    if message.message_id < len(data):
        # message was already added
        return
    data.append(message.message)
