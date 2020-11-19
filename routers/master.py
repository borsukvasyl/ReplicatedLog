import os

import requests
from fastapi import APIRouter

from routers.common import StatusModel, GetDataOutModel, AppendDataInModel

router = APIRouter()
data = []
secondaries = [f"http://{hostname}:8000" for hostname in os.environ["SECONDARIES"].split(":")]


@router.get("/status", response_model=StatusModel)
async def status():
    return StatusModel(status="OK")


@router.get("/get", response_model=GetDataOutModel)
async def get():
    return GetDataOutModel(messages=data)


@router.post("/append")
async def append(message: AppendDataInModel):
    data.append(message.message)

    for hostname in secondaries:
        response = requests.post(f"{hostname}/append", json=message.dict())
        if response.status_code != 200:
            raise ValueError(f"Cannot send [{data}] to secondary")
