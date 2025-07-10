from .devs.udpsensor import AIController
from .devs.modbus import LocalModbusDevice, ModbusDevice
from .devs.bacnet import LocalBACNetDevice, BACNetDevice

from ..db.models import Device
from ..utils.network import get_default_ip

class DeviceFactory:
    def __init__(self):
        self.proxy_devices = {}
    
    def get_or_create_proxy_device(self, device_type:str, property:dict=None):
        device_type = device_type.lower()
        if proxy_dev := self.proxy_devices.get(device_type):
            return proxy_dev
        if device_type == "bacnet":
            local_ipv4 = get_default_ip()
            print("local_ipv4=", local_ipv4)
            virtual_device_info = {
                "uid": "local_bacnet_device",
                "name": "local_bacnet_device",
                "protocol": "bacnet",
                "address":local_ipv4,
                "enabled": True,
                "property":{
                    "address":local_ipv4,
                    "port":47809,
                    "netmask":24
                }
            }
            proxy_dev = LocalBACNetDevice(Device(**virtual_device_info))
        elif device_type.startswith("modbusrtu"):  
            master_moudbus_info = {
                "uid": f"modbusrtu_{property['port']}",
                "name": f"modbusrtu_{property['port']}",
                "protocol": "modbusrtu",
                "address":247,
                "enabled": True,
                "property":property
            }
            proxy_dev = LocalModbusDevice(Device(**master_moudbus_info))
        else:
            raise ValueError(f"unsupported device type: {device_type}")
        
        self.proxy_devices[device_type] = proxy_dev
        return proxy_dev

    def create_device(self, device_metadata:Device):
        device_type = device_metadata.protocol.lower()
        if device_type == "modbusrtu":
            master_modbusrtu_uid = f"modbusrtu_{device_metadata.property['port']}"
            master_modbusrtu = self.get_or_create_proxy_device(master_modbusrtu_uid, device_metadata.property)
            if device_metadata.uid == master_modbusrtu_uid:
                return master_modbusrtu
            return ModbusDevice(device_metadata, master_modbusrtu)
        elif device_type == "modbustcp":
            return ModbusDevice(device_metadata)
        elif device_type == "bacnet":
            proxy_dev = self.get_or_create_proxy_device(device_type)
            if device_metadata.uid == "local_bacnet_device":
                return proxy_dev
            return BACNetDevice(device_metadata, proxy_dev)
        elif device_type == "udp":
            return AIController(device_metadata)
        else:
            raise ValueError(f"unsupported device type: {device_type}")