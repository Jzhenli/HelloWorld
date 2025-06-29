from typing import Any
from dataclasses import dataclass

from .base import BaseDevice
from ...log import logger
from ...models.device import DeviceRequest
from ...driver import AsyncUDPConnector
from ...db.models import Device, Metric
from ...db.utils import get_metrics_by_device, set_points


@dataclass
class AIDeviceProperty:
    host: str
    port: int

@dataclass
class AIDeviceRequest:
    cmd: str

class RequsetValidationError(ValueError):
    pass

class AIController(BaseDevice):
    def __init__(self, device:Device):
        self.device = device
        properties = AIDeviceProperty(**device.property)
        self.client = AsyncUDPConnector(host=properties.host, port=properties.port)
        self._error_cnt:int = 0
        self._max_retries = 60
        self.connected:bool = False

    def __repr__(self):
        return f"{self.device}"

    async def init(self):
        stop_cmd = {
            "function":"stop",
        }
        start_cmd = {
            "function":"start",
        }
        await self.handle_cmd(DeviceRequest(**stop_cmd))
        await self.handle_cmd(DeviceRequest(**start_cmd))
        logger.info(f"[AIDevice {self.device.uid}] run...")

    async def open(self):
        await self.client.open()
        logger.info(f"[AIDevice {self.device.uid}] connected")
        await self.init()

    async def close(self):
        await self.client.close()
        logger.info(f"[AIDevice {self.device.uid}] closed")

    async def _check_online(self):
        if not self.connected:
            await self.open()
            self.connected = True

    async def handle_cmd(self, request:DeviceRequest):
        status = "OK"
        ret = None
        try:
            cmd = request.function
            if args := request.parms.get("args"):
                cmd = f"{request.function},{args}"
            logger.debug("handle_cmd cmd=", cmd)
            command = cmd.encode('utf-8')
            await self.client.send(command)
            for _ in range(3):
                data, addr = await self.client.receive()
                rsp_str:str = data.decode('utf-8')
                ret = self._parse_sensor_data(rsp_str)
                logger.info(f"[AIDevice {self.device.uid}] excute {command}, Received {ret} from {addr}")
                if ret and ret["cmd"] not in cmd:
                    logger.error("-"*40)
                    status = "FAIL"
                else:
                    break
                
            self._error_cnt = 0
        except RequsetValidationError as ve:
            logger.error(f"ValidationError: {ve}")
            status = "INVALID_REQUEST"
        except UnicodeDecodeError as ude:
            logger.error(f"[{self.device.uid}] UnicodeDecodeError")
            status = "DATA_ERROR"
        except Exception as e:
            logger.error(f"[AIDevice {self.device.uid}] Error during handle_cmd: {e}")
            status = "FACONNECTION_ERRORIL" 
            self._handle_connection_error()   
 
        return {"status":status, "data":ret}


    async def sample(self):
        logger.debug("AI Controller smpling...")
        await self._check_online()
        metrics:list[Metric] = await get_metrics_by_device(self.device.id)
        points=[]
        for metric in metrics:
            try:
                request = {
                    "function":metric.property.get("function"),
                    "parms":{}
                }
                response = await self.handle_cmd(DeviceRequest(**request))
                if not response["status"] == "OK":continue
                if not response["data"]["status"]== "OK": continue
                if "None" in response["data"]["value"]: continue
                logger.info(f'{metric.uid} value {response["data"]["value"]}')
                values = response["data"]["value"].split(",")
                points.append(
                    {
                        "metric_id":metric.id,
                        "value":",".join(values[1:]),
                        "timestamp": int(values[0]),
                    }
                )
            except Exception as e:
                logger.error(f"AI Controller sample error {e}")

        await set_points(points)


    def _handle_connection_error(self):
        self._error_cnt = self._error_cnt + 1
        
        if self._error_cnt > self._max_retries:
            logger.critical(f"[{self.device.uid}] have failed reach {self._max_retries}")
            self.connected = False
            self._error_cnt = 0

    def _parse_sensor_data(self, data_string:str):
        ret = None
        try:
            rsp = data_string.split(",")
            ret = {
                "cmd": rsp[0],
                "status": rsp[1].upper(),
                "value": ",".join(rsp[2:])
            }
        except Exception as e:
            logger.error(f"Parsing error: Invalid string format: {data_string} - {e}")
        
        return ret
