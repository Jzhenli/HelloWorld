from datetime import datetime
import uuid
# from enum import Enum
from typing import List, Optional, Dict
from sqlmodel import Field, Relationship, SQLModel, JSON
from sqlalchemy import Column, ForeignKey
# from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON 
from pydantic import BaseModel
# class ProtocolType(str, Enum):
#     #MQTT = "MQTT"
#     MODBUS = "MODBUS"
#     BACNET = "BACNET"
#     UDP = "UDP"
#     OTHER = "OTHER"


class Device(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    uid: str = Field(index=True, unique=True)
    name: Optional[str] = Field(default=None)
    address: str
    protocol: str
    enabled: bool
    status: Optional[str] = Field(default=None)
    description: Optional[str] = None
    # property: Optional[dict] = Field(default=None, sa_column=Column(SQLiteJSON))
    property: Optional[Dict] = Field(default=None, sa_column=Column(JSON)) 
    tags: Optional[str] = Field(default=None)

    metrics: List["Metric"] = Relationship(back_populates="device", cascade_delete=True)
    

class Metric(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    uid: str = Field(index=True)
    name: Optional[str] = None
    description: Optional[str] = None
    property: Optional[Dict] = Field(default=None, sa_column=Column(JSON)) 
    tags: Optional[str] = None

    device_id: Optional[uuid.UUID]  = Field(default=None, foreign_key="device.id", ondelete="CASCADE")
    device: Optional[Device] = Relationship(back_populates="metrics")

    points: List["Point"] = Relationship(back_populates="metric", cascade_delete=True)


class Point(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    metric_id: Optional[uuid.UUID] = Field(default=None, index=True, foreign_key="metric.id", ondelete="CASCADE")
    value: str
    timestamp: int = Field(index=True) 
    property: Optional[Dict] = Field(default=None, sa_column=Column(JSON)) 
    tags: Optional[str] = None

    metric: Optional[Metric] = Relationship(back_populates="points") 


class Project(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    cover: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    time: datetime = datetime.now()

    