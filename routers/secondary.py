import os
import asyncio

from fastapi import APIRouter

from routers.common import NodeStatus, SecondaryStatusModel, GetDataOutModel, AppendDataInModel

router = APIRouter()
data = []
sleep = int(os.environ.get("SLEEP", 0))


@router.get("/health", response_model=SecondaryStatusModel)
async def health():
    return SecondaryStatusModel(status=NodeStatus.healthy)


@router.get("/get", response_model=GetDataOutModel)
async def get():
    return GetDataOutModel(messages=data)


@router.post("/append")
async def append(message: AppendDataInModel):
    await asyncio.sleep(sleep)
    data.append(message.message)
