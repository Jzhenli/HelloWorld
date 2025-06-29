import uuid
import glob
import platform
from fastapi import APIRouter, Depends
import serial.tools.list_ports

from .device import get_device
from ..schemas import ResponseModel, DakingWrite
from ...db.database import get_session, AsyncSession
from ...db.models import Device, Metric
from ...models.device import DeviceRequest, SettingRequest
from ...device import device_manager, BaseDevice
from .metric import get_metric_ids_by_names_daking

router = APIRouter(prefix="/iot", tags=["Action"])

@router.post("/setting", status_code=200)
async def metric_setting(metric_id:uuid.UUID, request:SettingRequest, session: AsyncSession = Depends(get_session)):
    metric = await session.get(Metric, metric_id)
    query_device = await get_device(metric.device_id, session)
    device:Device = query_device["data"]
    function_code = ""
    parms = {}
    if device.protocol.lower() in ["modbusrtu", "modbustcp"]:
        raw_function_code:str = metric.property.get("function")
        raw_parms:dict = metric.property.get("parms")
        function_map = {
            "01": "05",
            "03": "06"
        }
        function_code = function_map.get(raw_function_code, "")
        parms = raw_parms.copy()
        parms.pop("count")
        parms["value"] = request.value  
    elif device.protocol.lower()=="bacnet":
        function_code = "write_property"
        parms = {
            "address": device.address,
            "objid": metric.uid,
            "prop": "presentValue",
            "value": request.value
        }


    if function_code:
        request = {
            "function" : function_code,
            "parms": parms
        }
        ret = await device_request(device.id, DeviceRequest(**request), session)
        return ret

    return {"status":"FAIL", "data":f"unsupport {device.protocol}"}

@router.post("/request", status_code=200)
async def device_request(device_id:uuid.UUID, request:DeviceRequest, session: AsyncSession = Depends(get_session)):
    device = await session.get(Device, device_id)
    if not device:
        return {"status":"FAIL", "data":f"device {device_id} not found"}
    if not device.enabled:
        return {"status":"FAIL", "data":f"device {device_id} not enabled"}
    
    device_connector:BaseDevice= await device_manager.get_device(device_id) # type: ignore
    if not device_connector:
        await device_manager.add_device(device)
        device_connector:BaseDevice= await device_manager.get_device(device_id)

    if device_connector:
        ret = await device_connector.handle_cmd(request)
    else:
        ret = {"status":"FAIL", "data":f"device {device_id} not available"}
    return ret

@router.get("/bacnet/discovery", response_model=ResponseModel, status_code=200)
async def discovery_bacnet_device():
    try:
        local_bacnet_device = device_manager.get_proxy_device("bacnet")
        await local_bacnet_device.open()
        request = {
            "function":"discovery",
            "parms":{}
        }
        ret = await local_bacnet_device.handle_cmd(DeviceRequest(**request))
    except Exception as e:
        error_msg = f"discovery error {e}"
        ret = {"status":"FAIL", "data":error_msg}
    return ret

@router.post("/enable", response_model=ResponseModel, status_code=200)
async def enable_device(device_id: uuid.UUID, enable:bool, session: AsyncSession = Depends(get_session)):
    device = await session.get(Device, device_id)
    if not device: 
        return {"status":"FAIL", "data":f"{device_id} not found"}
    
    device.enabled = enable
    session.add(device)
    await session.commit()
    await session.refresh(device)

    if enable:
        pass
    else:
        pass

    return {"status":"OK", "data":device}


@router.get("/modbusrtu/ports")
async def read_modbusrtu_ports():
    status = "OK"
    data = []
    os_name = platform.system()
    if os_name == "Windows":
        ports = serial.tools.list_ports.comports()
        data = [port.device for port in ports]
    elif os_name == "Linux":
        data = glob.glob('/dev/ttyS*')
    else:
        status = "FAIL"
        data = "OS not support"
    return {"status":status, "data":data}


@router.post("/daking/points", status_code=200)
async def batch_set_daking_points(points: DakingWrite, session: AsyncSession = Depends(get_session)):
    try:
        status = "OK"
        pointnames = list(points.data.keys())
        point_info = await get_metric_ids_by_names_daking(pointnames, session)
        device:Device = point_info["data"]["device"]
        for point_item in point_info["data"]["metrics"]:
            # Implement the logic to read Daking points here
            name = point_item["name"]
            uid = point_item["uid"]
            value = points.data.get(name)
            request = {
                "function": "write_property",
                "parms": {
                    "address": device.address,
                    "objid": uid,
                    "prop": "present-value",
                    "value": value
                    }
            }
            await device_request(device.id, DeviceRequest(**request), session)

        return {"status": status, "data": ""}
    except Exception as e:
        status = "FAIL"
        return {"status": status, "data": f"Error: {e}"}