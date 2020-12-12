from typing import Any, List

from pydantic import BaseModel


class StatusModel(BaseModel):
    status: str


class GetDataOutModel(BaseModel):
    messages: List[Any]


class AppendDataInModel(BaseModel):
    message: Any


class AppendDataMasterInModel(AppendDataInModel):
    w: int = 1
