from enum import Enum
from typing import Any, List, Dict

from pydantic import BaseModel


class NodeStatus(str, Enum):
    healthy = "healthy"
    suspended = "suspended"
    unhealthy = "unhealthy"


class MasterStatusModel(BaseModel):
    statuses: Dict[str, NodeStatus]


class SecondaryStatusModel(BaseModel):
    status: NodeStatus


class GetDataOutModel(BaseModel):
    messages: List[Any]


class AppendDataInModel(BaseModel):
    message: Any


class AppendDataMasterInModel(AppendDataInModel):
    w: int = 1
