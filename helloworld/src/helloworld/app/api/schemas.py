from pydantic import BaseModel
from typing import Any, Optional, Dict
import uuid
import datetime


class ResponseModel(BaseModel):
    status: str
    data: Any

class DeviceCreate(BaseModel):
    uid: str
    name: Optional[str] = None
    address: str
    protocol: str
    enabled: Optional[bool] =False
    status: str
    property: Optional[dict] = None 
    tags: Optional[str] = None
    description: Optional[str] = None

class MetricCreate(BaseModel):
    uid: str
    name: Optional[str] = None
    property: Optional[dict] = None 
    tags: Optional[str] = None
    description: Optional[str] = None
    device_id: uuid.UUID

class PointCreate(BaseModel):
    metric_id: uuid.UUID
    value: str
    timestamp: datetime.datetime
    property: Optional[dict] = None
    tags: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str
    cover: Optional[str] = None
    content: str
    description: Optional[str] = None


class DakingWrite(BaseModel):
    data: Dict[str, Any] 