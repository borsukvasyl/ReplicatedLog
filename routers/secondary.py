import os
import time

from fastapi import APIRouter

from routers.common import StatusModel, GetDataOutModel, AppendDataInModel

router = APIRouter()
data = []
sleep = int(os.environ.get("SLEEP", 0))


@router.get("/health", response_model=StatusModel)
async def health():
    return StatusModel(status="OK")


@router.get("/get", response_model=GetDataOutModel)
async def get():
    return GetDataOutModel(messages=data)


@router.post("/append")
async def append(message: AppendDataInModel):
    time.sleep(sleep)
    data.append(message.message)
