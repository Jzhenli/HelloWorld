import asyncio
import re
from typing import Optional, List, Optional, Tuple, Union, Dict, Any
from bacpypes3.pdu import Address
from bacpypes3.app import Application
from bacpypes3.local.device import DeviceObject
from bacpypes3.local.networkport import NetworkPortObject
from bacpypes3.primitivedata import ObjectIdentifier, PropertyIdentifier
from bacpypes3.apdu import AbortReason, AbortPDU, ErrorRejectAbortNack
from bacpypes3.basetypes import ErrorType, PriorityValue

from ...log import logger

class BacnetClientException(Exception):
    pass



# def convert_name(input_string):
#   """
#   将字符串中的大写字母变为小写，并在该字母前加"-", 比如"outOfService"变成“out-of-service”

#   Args:
#     input_string: 输入的字符串, 如“outOfService”

#   Returns:
#     转换后的字符串， 如“out-of-service”
#   """
#   return re.sub(r"([A-Z])", r"-\1", input_string).lower().lstrip('-')

class BacnetClient:
    def __init__(self, local_ip: str, local_port: int = 47808, netmask:int = 24):
        """
        Init BACnet client
        :param local_ip: ip address
        :param local_port: default 47809
        :netmask: default 24
        """
        self.local_address = f"{local_ip}/{netmask}:{local_port}"
        self.app: Optional[Application] = None
        self.discovered_devices: List[dict] = []
        self._running = False

    async def open(self) -> None:
        if self._running:
            return

        try:
            device_object = DeviceObject(
                objectIdentifier=("device", 999),
                objectName='XNode BACnet Device',
                maxApduLengthAccepted=1024,
                vendorIdentifier=999,
                modelName="XNode BACnet Simulator",
                vendorName = 'Adveco',
                firmwareRevision = "N/A",
            )

            network_port_object = NetworkPortObject(
                self.local_address,
                objectIdentifier=("networkPort", 1),
                objectName="Network Port 1",
            )
            # network_port_object.debug_contents()
            self.app = Application.from_object_list([device_object, network_port_object]) # type: ignore
            self._running = True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Connection failed: {e}")

    async def close(self):
        if self.app:
            self.app.close()
            self.app = None
        self._running = False

    async def discovery(self, timeout: int = 3) -> List[dict]:
        """
        discovery device
        :param timeout: 响应超时时间（秒）
        :return: 发现的设备列表
        """
        if not self._running:
            raise RuntimeError("Connection not open")
        
        self.discovered_devices.clear()
        i_ams = await self.app.who_is(timeout=timeout)
        for i_am in i_ams:
            device_address: Address = i_am.pduSource
            device_identifier: ObjectIdentifier = i_am.iAmDeviceIdentifier
            print("-"*30)
            print(f"{device_identifier} @ {device_address}, addrNetworkType : {device_address.addrNetworkType}")
 
            bacnet_device = {
                "id": f"{device_identifier}",
                "addr": f"{device_address}",
                "type": device_address.addrNetworkType,
            }
            
            try:
                parameter_list = [f"{device_identifier}", ["objectName", "modelName", "vendorName","applicationSoftwareVersion"]]
                response = await self.read_property_multiple(device_address, parameter_list)
                for (
                    object_identifier,
                    property_identifier,
                    property_array_index,
                    property_value,
                ) in response:
                    if property_array_index is not None:
                        print(f"{object_identifier} {property_identifier}[{property_array_index}] {property_value}")
                    else:
                        print(f"{object_identifier} {property_identifier} {property_value}")
                        bacnet_device[f"{property_identifier}"] = f"{property_value}"
                    if isinstance(property_value, ErrorType):
                        print(f"    {property_value.errorClass}, {property_value.errorCode}")
                
                self.discovered_devices.append(bacnet_device)
            except Exception as e:
                logger.error(f"{device_identifier} discovery error: {e}.")
                raise BacnetClientException(f"discovery error: {e}.")

        return self.discovered_devices

    async def read_property(
        self,
        address: Union[Address, str],
        objid: Union[ObjectIdentifier, str],
        prop: Union[PropertyIdentifier, str],
        array_index: Optional[int] = None,
    ) -> Any:
        """
        Send a Read Property Request to an address and decode the response,
        returning just the value, or the error, reject, or abort if that
        was received.
        """
        if not self._running:
            raise RuntimeError("Bacnet device not running.")
        
        property_value = None
        try:
            property_value = await self.app.read_property(
                address, objid, prop, array_index
            )
            if PropertyIdentifier(prop) == 87:
                property_value = self.serialize_priority_array(property_value)
        except ErrorRejectAbortNack as e:
            logger.error(f"read_property {address} {objid} {prop} error: {e}.")
            raise BacnetClientException(f"read_property error: {e}.")
        except Exception as e:
            raise BacnetClientException(f"read_property exception: {e}.")

        return property_value
    
    async def read_object_list(
        self,
        device_address: Union[Address, str],
        device_identifier: Union[ObjectIdentifier, str]
    ) -> List[ObjectIdentifier]:
        """
        Read the entire object list from a device at once, or if that fails, read
        the object identifiers one at a time.
        """
        if not self._running:
            raise RuntimeError("Connection not open")
        object_list = []
        # try reading the whole thing at once, but it might be too big and
        # segmentation isn't supported
        try:
            object_list = await self.app.read_property(
                device_address, device_identifier, "object-list"
            )
        except AbortPDU as err:
            logger.error(f"{device_identifier} object-list abort: {err.apduAbortRejectReason}.")
            if err.apduAbortRejectReason != AbortReason.segmentationNotSupported:
                return []
        except ErrorRejectAbortNack as err:
            logger.error(f"{device_identifier} object-list error reject: {err}.")
            return []
        except Exception as err:
            logger.error(f"{device_identifier} object-list error: {err}.")

        if object_list: return object_list
        # fall back to reading the length and each element one at a time
        try:
            # read the length
            object_list_length = await self.read_property(
                device_address,
                device_identifier,
                "object-list",
                array_index=0,
            )
            # read each element individually
            for i in range(object_list_length):
                object_identifier = await self.read_property(
                    device_address,
                    device_identifier,
                    "object-list",
                    array_index=i + 1,
                )
                object_list.append(object_identifier)
        except Exception as err:
            logger.error(f"{device_identifier} object-list one by one error: {err}.")
 
        return object_list

    async def read_property_multiple(
        self,
        device_address: Address,
        parameter_list: List[
            Tuple[
                Union[ObjectIdentifier, str],
                List[Union[PropertyIdentifier, str]],
            ],
        ],
    ) -> List[Tuple[ObjectIdentifier, PropertyIdentifier, Union[int, None], Any]]:
        if not self._running:
            raise RuntimeError("Bacnet device not running.")
        response = []

        try:
            response = await self.app.read_property_multiple(device_address, parameter_list)
            # response = [self._modify_property_tuple(t) for t in raw_response]
            # return response
        except ErrorRejectAbortNack as e:
            logger.error(f"read_property_multiple error: {e}.")
            # raise BacnetClientException(f"{e}")
        except Exception as e:
            logger.error(f"read_property_multiple error: {e}.")
            raise BacnetClientException(f"{e}")
        
        if not response:
            for objid, pros in zip(parameter_list[::2], parameter_list[1::2]):
                tasks = [self.read_property(device_address, objid, pro) for pro in pros]
                rsp = await asyncio.gather(*tasks, return_exceptions=True)
                ret = [
                        [
                            ObjectIdentifier(objid),
                            PropertyIdentifier(pro),
                            None,
                            rsp[i]
                        ] for i, pro in enumerate(pros)
                ]
                response.extend(ret)

        rsp = [self._check_property_tuple(t) for t in response]

        return rsp

    async def write_property(
        self,
        device_address: Union[Address, str],
        object_id: Union[ObjectIdentifier, str],
        property_id: Union[PropertyIdentifier, str],
        value: Any,
        property_array_index: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> Any:
        """
        Send a Write Property Request to an address and expect a simple
        acknowledgement.  Return the error, reject, or abort if that
        was received.
        :param device_address: str
        :param object_id: str
        :param property_id: str
        :param value: to write
        :param property_array_index:
        :param priority
        :return: Return the error, reject, or abort if that was received.
        """
        if not self._running:
            raise RuntimeError("Connection not open")
        
        try:
            response = await self.app.write_property(
                address=device_address,
                objid=object_id,
                prop=property_id,
                value=value,
                array_index=property_array_index,
                priority=priority
            )
        except ErrorRejectAbortNack as e:
            logger.error(f"write_property error: {e}.")
            raise BacnetClientException(f"{e}")

        return response
    
    def _modify_property_tuple(self, item:set):
        oid, pid, pindex, pvalue = item
        if isinstance(pvalue, ErrorType):
            return (oid, pid, pindex, str(pvalue.errorCode))
        else:
            return item
        
    def _check_property_tuple(self, item:set):
        oid, pid, pindex, pvalue = item
        if isinstance(pvalue, ErrorType):
            return (oid, pid, pindex, str(pvalue.errorCode))
        elif pid == 87 and isinstance(pvalue, list):
            return (oid, pid, pindex, self.serialize_priority_array(pvalue))
        return item
        
    def serialize_priority_array(self, priority_array:list[PriorityValue]):
        priority_array_dict: Dict[int, Any] = {}
        try:
            for index, item in enumerate(priority_array):
                priority_level = index + 1
                data_type = item._choice
                if data_type == "null":
                    priority_array_dict[priority_level] = None
                else:
                    if hasattr(item, item._choice):
                        value_object = getattr(item, item._choice)
                        priority_array_dict[priority_level] = value_object
                    else:
                        priority_array_dict[priority_level] = None
        except:
            priority_array_dict = {key: None for key in range(1, 17)}
        return priority_array_dict
    

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def test():
    async with BacnetClient(local_ip="192.168.20.210") as client:
        # 设备发现
        devices = await client.discovery()
        print(f"发现 {len(devices)} 个设备:")
        for dev in devices:
            print(dev)
            try:
                description: str = await client.read_property(
                    dev["addr"], dev["id"], "description"
                )
                print("description=",description)
            except Exception as e:
                print("description error:",str(e))

if __name__ == "__main__":
    asyncio.run(test())