import uuid
from ..schemas import ResponseModel, MetricCreate
from ...db.database import get_session, AsyncSession
from ...db.models import Metric, Device
from ...utils.check import starts_with_any_prefix

from typing import List
from sqlmodel import select, delete
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/iot", tags=["Metric"])


@router.post("/metric", response_model=ResponseModel, status_code=200)
async def create_metric(metric: MetricCreate, session: AsyncSession = Depends(get_session)):
    db_metric = Metric.model_validate(metric)
    try:
        session.add(db_metric)
        await session.commit()
        await session.refresh(db_metric)
        return {"status":"OK", "data":db_metric}
    except Exception as e:
        await session.rollback()
        return {"status":"FAIL", "data":"metric already exists"}

@router.get("/metric/{metric_id}", response_model=ResponseModel, status_code=200)
async def get_metric(metric_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    metric = await session.get(Metric, metric_id)
    return {"status":"OK", "data":metric}

@router.patch("/metric/{metric_id}", response_model=ResponseModel, status_code=200)
async def update_metric(metric_id: uuid.UUID, metric_update: dict, session: AsyncSession = Depends(get_session)):
    metric = await session.get(Metric, metric_id)
    if not metric: return {"status":"FAIL", "data":f"{metric_id} not found"}

    for key, value in metric_update.items():
        setattr(metric, key, value)
    session.add(metric)
    await session.commit()
    await session.refresh(metric)
    return {"status":"OK", "data":metric}

@router.delete("/metric/{metric_id}", response_model=ResponseModel, status_code=200)
async def delete_metric(metric_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    metric = await session.get(Metric, metric_id)
    if metric:
        await session.delete(metric)
        await session.commit()
        return {"status":"OK", "data":metric}
    return {"status":"FAIL", "data":f"{metric_id} not found"}

@router.get("/metrics/{device_id}", response_model=ResponseModel, status_code=200)
async def get_all_metrics_by_device(device_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Metric).where(Metric.device_id==device_id))
    metrics = result.scalars().all()
    return {"status":"OK", "data":list(metrics)}

@router.get("/metrics", response_model=ResponseModel, status_code=200)
async def get_all_metrics(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Metric))
    metrics = result.scalars().all()
    return {"status":"OK", "data":list(metrics)}

@router.post("/metrics", response_model=ResponseModel, status_code=200)
async def batch_create_metrics(metrics: List[MetricCreate], session: AsyncSession = Depends(get_session)):
    try:
        # db_metrics = [Metric.model_validate(metric) for metric in metrics]
        db_metrics = []
        for metric in metrics:
            if not starts_with_any_prefix(metric.name):
                continue
            try:
                db_metrics.append(Metric.model_validate(metric))
            except:
                continue

        session.add_all(db_metrics)
        await session.commit()
        for metric in db_metrics:
            await session.refresh(metric)
        return {"status":"OK", "data":db_metrics}
    except Exception as e:
        await session.rollback()
        print(f"batch_create_metrics error {e}")
        return {"status":"FAIL", "data":"some metric already exists"}

@router.delete("/metrics/{device_id}", response_model=ResponseModel, status_code=200)
async def delete_all_metrics_for_device(device_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    try:
        statement = delete(Metric).where(Metric.device_id == device_id)
        await session.execute(statement)
        await session.commit()
        return {"status":"OK", "data":f"delete all metrics for {device_id}."}
    except Exception as e:
        await session.rollback()
        return {"status":"FAIL", "data":f"{e}"}


@router.delete("/metrics", response_model=ResponseModel, status_code=200)
async def batch_delete_metrics(metric_ids: List[uuid.UUID], session: AsyncSession = Depends(get_session)):
    del_ids=[]
    for metric_id in metric_ids:
        metric = await session.get(Metric, metric_id)
        if metric:
            await session.delete(metric)
            del_ids.append(metric_id)
    await session.commit()
    return {"status":"OK", "data":del_ids}


@router.post("/metrics/ids", response_model=ResponseModel, status_code=200)
async def get_metric_ids_by_names_daking(
    names: List[str],
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Metric).where(Metric.name.in_(names))
    )
    metrics = result.scalars().all()
    metrics_data = [{"name": m.name, "uid": m.uid} for m in metrics]
    device = await session.get(Device, metrics[0].device_id)
    data = {
        "device": device,
        "metrics": metrics_data
    }
    return {"status": "OK", "data": data}


