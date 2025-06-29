# models/device.py
from dataclasses import dataclass,field
from typing import Dict, List, Optional, List, Any

# @dataclass
# class DeviceProperty:
#     identifier: str
#     name: str
#     data_type: str
#     access_mode: str
#     unit: Optional[str] = None
#     min_value: Optional[float] = None
#     max_value: Optional[float] = None
#     current_value: Any = None


# @dataclass
# class DeviceEvent:
#     event_type: str
#     event_code: str
#     timestamp: float
#     payload: Any

# @dataclass
# class DeviceService:
#     service_id: str
#     name: str
#     input_params: List[dict]
#     output_params: List[dict]
#     description: str = ""

# @dataclass
# class DeviceMetadata:
#     device_id: str
#     device_type: str
#     protocol_type: str
#     description: Optional[str] = None
#     manufacturer: Optional[str] = None
#     properties: List[DeviceProperty] = None
#     services: List[DeviceService] = None
#     events: List[DeviceEvent] = None
#     connection_params: Dict = None
#     status: str = 'offline'

# @dataclass
# class DeviceBase:
#     device_addr: str
#     device_type: str
    

# @dataclass
# class Device:
#     device_id: str
#     protocol: str
#     enabled: bool = 0
#     polling: int = 3
#     device_name: Optional[str] = None
#     status: Optional[str] = ""
#     properties: Optional[Dict] = field(default_factory=dict)
#     tags: Optional[Dict] = field(default_factory=dict)


# @dataclass
# class Metric:
#     metric_id: str
#     device_id: str
#     data_type: str  # 放到前面，因为它没有默认值
#     metric_name: Optional[str] = None
#     unit: Optional[str] = None
#     description: Optional[str] = None
#     properties: Optional[Dict] = field(default_factory=dict)
#     tags: Optional[Dict] = field(default_factory=dict)


# @dataclass
# class Point:
#     device_id: str
#     metric_id: str
#     value: str
#     timestamp: int = 0
#     properties: Optional[Dict] = field(default_factory=dict)
#     tags: Optional[Dict] = field(default_factory=dict)


@dataclass
class ModbusProperty:
    slaveid: int
    port: str
    baudrate: int = 9600
    bytesize: int = 8
    stopbits: int = 1
    parity: str = "N"
    connectionOption:str="SerialPort" #"TcpPort"

@dataclass
class ModbusTCPProperty:
    host: str
    port: int
    connectionOption:str="TCP" #"TcpPort"

@dataclass
class ModbusReadRequest:
    address: int
    count: int = 1
    data_type: str = "int16"
    byteorder: int = 0
    wordorder: int = 0
    divisor: int = 1


@dataclass
class ModbusWriteRequest:
    address: int
    value: Any
    data_type: str = "int16"
    byteorder: int = 0
    wordorder: int = 0
    divisor: int = 1


@dataclass
class QueryPoint:
    device_id: str
    metric_id: str
    start_time:int = 0
    end_time: int = 0


@dataclass
class DeviceRequest:
    # device_id: str
    function: str
    parms: Optional[Dict] = field(default_factory=dict)

@dataclass
class SettingRequest:
    # device_id: str
    value: Any