from .base import BaseDevice
from ...driver import AsyncBACNetConnector
from ...log import logger
from ...models.device import DeviceRequest
from ...db.models import Device, Metric, Point
from ...db.utils import get_metrics_by_device, set_points
from ...cache import aiocache

import time
import asyncio
import json
from dataclasses import dataclass
from typing import Optional, Any
from bacpypes3.basetypes import ErrorType

@dataclass
class PropertyQuery:
    address: str
    objid: str
    prop: str
    index: Optional[int] = None

@dataclass
class MutiPropertyQuery:
    address: str
    read_list: list

@dataclass
class ObjListQuery:
    address: str
    objid: str

@dataclass
class PropertyWrite:
    address: str
    objid: str
    prop: str
    value: Any
    index: Optional[int] = None
    priority: Optional[int] = None


class LocalBACNetDevice(BaseDevice):
    def __init__(self, device:Device):
        self.device = device
        self.client:AsyncBACNetConnector = AsyncBACNetConnector(self.device.address)
        
    def __repr__(self):
        return f"{self.device}"

    async def open(self):
        await self.client.open()
        logger.info(f"设备 {self.device.uid} 连接成功")

    async def close(self):
        await self.client.close()
        logger.info(f"设备 {self.device.uid} 关闭成功")

    async def handle_cmd(self, request:DeviceRequest):
        status = "OK"
        try:
            function = request.function
            parms = request.parms
            if function=="discovery":
                rsp = await self.client.discovery()
                logger.debug(f"rsp={rsp}")
            elif function=="read_object_list":
                args = ObjListQuery(**parms) # type: ignore
                rsp = await self.client.read_object_list(
                    device_address=args.address,
                    device_identifier=args.objid
                )
            elif function=="read_property":
                args = PropertyQuery(**parms) # type: ignore
                rsp = await self.client.read_property(
                    address=args.address, 
                    objid=args.objid, 
                    prop=args.prop, 
                    array_index=args.index
                )
            elif function=="read_property_multiple":
                args = MutiPropertyQuery(**parms) # type: ignore
                rsp = await self.client.read_property_multiple(
                    device_address=args.address, # type: ignore
                    parameter_list=args.read_list
                )
            elif function=="write_property":
                args = PropertyWrite(**parms) # type: ignore
                print(f"write_property  args={args}")
                rsp = await self.client.write_property(
                    device_address=args.address,
                    object_id=args.objid,
                    property_id=args.prop,
                    value=args.value,
                    property_array_index=args.index,
                    priority=args.priority
                )
                print(f"write_property rsp={rsp}")
            else:
                status = "FAIL"
                rsp = f"unsupport {function}"
        except Exception as e:
            status = "FAIL"
            rsp = f"Error {e}"
        
        if not status == "OK": logger.error(rsp)

        return {"status":status, "data":rsp}

    async def sample(self):
        pass

    
class BACNetDevice(BaseDevice):
    def __init__(self, device:Device, client:LocalBACNetDevice):
        self.device = device
        self.client:LocalBACNetDevice = client

    def __repr__(self):
        return f"{self.device}"
    
    async def open(self):
        await self.client.open()
        logger.info(f"设备 {self.device.uid} 连接成功")

    async def close(self):
        logger.info(f"设备 {self.device.uid} 关闭成功")

    async def handle_cmd(self, request:DeviceRequest):
        logger.debug("BACNetDevice handle_cmd request=", request)
        rsp = await self.client.handle_cmd(request)
        logger.debug("BACNetDevice handle_cmd rsp=",rsp)
        return rsp

    async def sample(self, ttl:int):
        logger.info(f"BACNet Device {self.device.name} sample.....")
        metrics:list[Metric] = await get_metrics_by_device(self.device.id)
        points = []
        for metric in metrics:
            try:
                logger.debug(f"metric.metric_name:{metric.name}")
                pro_list:list = metric.property.get("pro_list") # type: ignore
                if not pro_list: continue
                request = {
                    "function":"read_property_multiple",
                    "parms":{
                        "address":self.device.address, 
                        "read_list":[metric.uid, pro_list]
                    }
                }
                response = await self.handle_cmd(DeviceRequest(**request))
                if not response["status"] == "OK":continue
                pros = {str(pro_id):pro_value for (obj_id,pro_id,pro_index,pro_value) in response["data"]}
                logger.debug(f"metric.value:{pros}")
                points.append(
                    {
                        "metric_id":metric.id,
                        "value":pros.get("present-value", ""),
                        "timestamp": int(time.time()),
                        "property":pros,
                        "tags":metric.name
                    }
                )
                # await asyncio.sleep(0.005)
            except Exception as e:
                logger.info(f"BACNetDevice sample error {e}")

        if points:
            await aiocache.mset({point["metric_id"]: point for point in points}, ttl=2*int(ttl))
  
        return True
           


