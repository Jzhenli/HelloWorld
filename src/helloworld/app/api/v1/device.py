import uuid
from ..schemas import ResponseModel, DeviceCreate
from ...db.database import get_session, AsyncSession
from ...db.models import Device

from typing import List
from sqlmodel import select, insert
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/iot", tags=["Device"])


@router.post("/device", response_model=ResponseModel, status_code=200)
async def create_device(device: DeviceCreate, session: AsyncSession = Depends(get_session)):
    db_device = Device.model_validate(device)
    try:
        session.add(db_device)
        await session.commit()
        await session.refresh(db_device)
        return {"status":"OK", "data":db_device}
    except Exception as e:
        await session.rollback()
        print(f"create_device error {e}")
        return {"status":"FAIL", "data":"device already exists"}

@router.get("/device/{device_id}", response_model=ResponseModel, status_code=200)
async def get_device(device_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    device = await session.get(Device, device_id)
    return {"status":"OK", "data":device}

@router.patch("/device/{device_id}", response_model=ResponseModel, status_code=200)
async def update_device(device_id: uuid.UUID, device_update: dict, session: AsyncSession = Depends(get_session)):
    device = await session.get(Device, device_id)
    if not device: 
        return {"status":"FAIL", "data":f"{device_id} not found"}

    for key, value in device_update.items():
        setattr(device, key, value)
    session.add(device)
    await session.commit()
    await session.refresh(device)
    return {"status":"OK", "data":device}

@router.delete("/device/{device_id}", response_model=ResponseModel, status_code=200)
async def delete_device(device_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    device = await session.get(Device, device_id)
    if device:
        await session.delete(device)
        await session.commit()
        return {"status":"OK", "data":device}
    return {"status":"FAIL", "data":f"{device_id} not found"}

@router.get("/devices", response_model=ResponseModel, status_code=200)
async def get_all_devices(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Device))
    devices = result.scalars().all()
    return {"status":"OK", "data":list(devices)}

@router.post("/devices", response_model=ResponseModel, status_code=200)
async def batch_create_devices(devices: List[DeviceCreate], session: AsyncSession = Depends(get_session)):
    try:
        db_devices = [Device.model_validate(device) for device in devices]
        session.add_all(db_devices)
        await session.commit()
        for device in db_devices:
            await session.refresh(device)
        return {"status":"OK", "data":db_devices}
    except Exception as e:
        await session.rollback()
        print(f"batch_create_devices error {e}")
        return {"status":"FAIL", "data":"some device already exists"}

@router.delete("/devices", response_model=ResponseModel, status_code=200)
async def batch_delete_devices(device_ids: List[uuid.UUID], session: AsyncSession = Depends(get_session)):
    del_ids=[]
    for device_id in device_ids:
        device = await session.get(Device, device_id)
        if device: 
            await session.delete(device)
            del_ids.append(device_id)
    await session.commit()
    return {"status":"OK", "data":del_ids}