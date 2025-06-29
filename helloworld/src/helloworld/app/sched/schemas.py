from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict

config = ConfigDict(
    json_schema_extra={
        "example": {
            "func": "example.main:pytest_job", 
            "trigger": "interval", 
            "seconds": 3, 
            "id": "pytest_job"
        }
    }
) # type: ignore


class TriggerEnum(str, Enum):
    interval = "interval"
    cron = "cron"
    date = "date"


class Job(BaseModel):
    # model_config = config
    func: str = Field()  # TODO: PyObject https://github.com/pydantic/pydantic/issues/4079
    trigger: TriggerEnum = Field(title="Trigger type")
    seconds: int = Field(title="Interval in seconds")
    id: str = Field(title="Job ID")
    kwargs : Dict = Field(default_factory=dict, title="Job parameter, default is None")


class JobNotFoundError(Exception):
    pass