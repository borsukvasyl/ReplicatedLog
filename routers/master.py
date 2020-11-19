import os

import grequests
from fastapi import APIRouter, status

from routers.common import StatusModel, GetDataOutModel, AppendDataInModel

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
async def append(message: AppendDataInModel):
    data.append(message.message)

    requests = [grequests.post(f"{hostname}/append", json=message.dict()) for hostname in secondaries]
    responses = grequests.map(requests)
    for response, hostname in zip(responses, secondaries):
        if response is None or response.status_code != status.HTTP_200_OK:
            raise ValueError(f"Failed to replicate on [{hostname}]")
