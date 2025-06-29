import time
import asyncio
from .base import BaseDevice
from ...driver import AsyncModbusConnector
from ...log import logger
from ...db.models import Device, Metric, Point
from ...models.device import ModbusProperty, ModbusReadRequest, ModbusWriteRequest, DeviceRequest
from ...db.utils import get_metrics_by_device, set_points
from ...cache import aiocache


class LocalModbusDevice(BaseDevice):
    def __init__(self, device:Device):
        self.device = device
        # connect_parms = ModbusProperty(**self.device.property)
        self.client = AsyncModbusConnector(self.device.property)
        
    def __repr__(self):
        return f"{self.device}"

    async def open(self):
        await self.client.open()
        logger.info(f"device {self.device.name} open.")

    async def close(self):
        await self.client.close() # type: ignore
        logger.info(f"device {self.device.name} close.")

    async def handle_cmd(self, slave:int, request:DeviceRequest):
        function = request.function
        parms = request.parms
        function_map = {
            "01": self.client.read_coils,
            "02": self.client.read_discrete_inputs,
            "03": self.client.read_holding_registers,
            "04": self.client.read_input_registers,
            "05": self.client.write_coil,
            "06": self.client.write_register
        }
        status = "OK"
        try:
            if function in ['01', '02', '03', '04']:
                if isinstance(parms, list):
                    req = [ModbusReadRequest(**item) for item in parms]
                else:
                    req = [ModbusReadRequest(**parms)]
            elif function in ['05', '06']:
                req = ModbusWriteRequest(**parms)
            else:
                req = parms
                
            if func := function_map.get(function):
                rsp = await func(slave, req)
            else:
                rsp = f"unsupport {function}"
                status = "FAIL"
        except Exception as e:
            status = "FAIL"
            rsp = f"execut {function} error {e}"

        return {"status":status, "data":rsp}

    async def sample(self):
        pass


class ModbusDevice(BaseDevice):
    def __init__(self, device:Device, client:LocalModbusDevice = None):
        self.device = device
        self.client:LocalModbusDevice = client
        
    def __repr__(self):
        return f"{self.device}"

    async def open(self):
        if self.client is None:
            self.client=LocalModbusDevice(self.device)
        await self.client.open()
        
    async def close(self):
        await self.client.close() # type: ignore

    async def handle_cmd(self, request:DeviceRequest):
        rsp = await self.client.handle_cmd(slave=int(self.device.address),request=request)
        return {"status":rsp["status"], "data":rsp["data"]}


    async def sample(self, ttl:int):
        logger.info(f"Modbus Device {self.device.uid} sample.....")
        metrics:list[Metric] = await get_metrics_by_device(self.device.id)
        function_code_groups:dict[str, list] = {}
        metric_map:dict[str, tuple] ={}
        for metric in metrics:
            function_code = metric.property.get("function")
            parms:dict =  metric.property.get("parms")
            if (not function_code) or (not parms): continue
            metric_address = parms.get("address")
            metric_map[metric_address] = (metric.id, metric.name)
            if function_code not in function_code_groups:
                function_code_groups[function_code] = [parms]
            else:
                function_code_groups[function_code].append(parms)

        points = []
        for key, value in function_code_groups.items():
            request = {
                "function":key,
                "parms": value
            }
            response = await self.handle_cmd(DeviceRequest(**request))
            logger.debug(f"Modbus Device {self.device.uid} response: {response}")
            if not response["status"] == "OK":continue
            for item in response["data"]:
                adress = item["address"]
                points.append(
                    {
                        "metric_id":metric_map[adress][0],
                        "value":str(item["value"]),
                        "timestamp": int(time.time()),
                        "property":{},
                        "tags":metric_map[adress][1]
                    }
                )

        if points:
            # await set_points(points)
            await aiocache.mset({point["metric_id"]: point for point in points}, ttl=2*int(ttl))
            # logger.info(f"Modbus Device {self.device.uid} sample points: {points}")

        return True
        
        

