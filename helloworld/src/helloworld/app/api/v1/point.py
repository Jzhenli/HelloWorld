import uuid
import time
from ..schemas import ResponseModel, PointCreate
from ...db.database import get_session, AsyncSession
from ...db.models import Point, Metric
from ...cache import aiocache

from typing import List
from sqlmodel import select, delete, func
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/iot", tags=["Point"])


def handle_points(points:dict):
    """Handles the creation of points and returns a list of dictionaries."""
    points_list = []
    for id, point in points.items():
        if point is None:
            point = {
                "metric_id": id,
                "value": None,
                "status": 0,
                "timestamp": int(time.time())
            }
        else:
            point["status"] = 1
        points_list.append(point)
    return points_list

@router.post("/points/newest", response_model=ResponseModel, status_code=200)
async def read_latest_points_for_metrics(metric_ids:List[uuid.UUID]):
    """Retrieves the latest value for each metric."""
    points_dict:dict = await aiocache.mget(metric_ids)
    points = handle_points(points_dict)
    return {"status": "OK", "data": points}

@router.get("/points/latest", response_model=ResponseModel, status_code=200)
async def get_each_metric_latest_value_by_device(device_id:uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Retrieves the latest value for each metric from the Point table."""
    statement = select(Metric).where(Metric.device_id == device_id)
    results = await session.execute(statement)
    metric_id_list:list = [Metric.id for Metric in results.scalars().all()]
    points_dict:dict = await aiocache.mget(metric_id_list)
    points = handle_points(points_dict)
    return {"status":"OK", "data":points}