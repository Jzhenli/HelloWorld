import uuid
import asyncio
from typing import Dict, List, Optional, Any

from ..log import logger
from .devs import BaseDevice
from .factory import DeviceFactory
from ..db.utils import get_all_devices
from ..db.models import Device

class DeviceManager:
    def __init__(self):
        self._factory = DeviceFactory()
        self._devices: Dict[uuid.UUID, BaseDevice] = {}
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        raw_list:list[Device] = await get_all_devices()
        for meta in raw_list:
            try:
                if meta.enabled:
                    device = self._factory.create_device(meta)
                    await device.open()
                    self._devices[meta.id] = device # type: ignore
                    logger.info(f"device [{meta.id}] init OK.")  
                else:
                    logger.info(f"skip device [{meta.id}] because not enabled.")
            except Exception as e:
                logger.error(f"device[{meta.id}] init FAIL: {e}")
        logger.info("DeviceManager start")

    async def stop(self) -> None:
        async with self._lock:
            for dev_id, device in list(self._devices.items()):
                try:
                    await device.close()
                    logger.info(f"device [{dev_id}] close OK.")
                except Exception as e:
                    logger.error(f"device[{dev_id}] close FAIL: {e}")
            self._devices.clear()
        logger.info("DeviceManager stop")

    async def add_device(self, meta: Device) -> Dict[str, Any]:
        async with self._lock:
            if meta.id in self._devices:
                return self._response("FAIL", "device exists")
            try:
                device = None
                if meta.enabled:
                    device = self._factory.create_device(meta)
                    await device.open()
                    self._devices[meta.id] = device # type: ignore
                    logger.info(f"device [{meta.id}] init OK.")
                else:
                    logger.info(f"skip device [{meta.id}] because not enabled.")
                return self._response("OK", device)
            except Exception as e:
                logger.error(f"device[{meta.id}] init FAIL: {e}")
                return self._response("FAIL", "device open error")

    async def remove_device(self, device_id: uuid.UUID) -> Dict[str, Any]:
        async with self._lock:
            device = self._devices.get(device_id)
            if not device:
                return self._response("FAIL", "device not exist")
            try:
                await device.close()
            except Exception as e:
                logger.error(f"device [{device_id}] close error: {e}")
            self._devices.pop(device_id, None)

        logger.info(f"device [{device_id}] have removed")
        return self._response("OK")

    async def get_device(self, device_id: uuid.UUID) -> Optional[BaseDevice]:
        return self._devices.get(device_id)

    def get_proxy_device(self, device_type: str) -> Optional[BaseDevice]:
        try:
            return self._factory.get_or_create_proxy_device(device_type)
        except Exception as e:
            logger.error(f"get_proxy_device({device_type}) error: {e}")
            return None

    def _response(self, status: str, data: Any = None) -> Dict[str, Any]:
        resp = {"status": status}
        if data is not None:
            resp["data"] = data
        return resp