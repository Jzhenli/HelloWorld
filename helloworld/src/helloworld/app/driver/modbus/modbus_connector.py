import pymodbus.client as ModbusClient
from pymodbus import (
    FramerType,
    ModbusException,
    pymodbus_apply_logging_config,
)

pymodbus_apply_logging_config("ERROR")

from dataclasses import asdict
from .exceptions import ModbusRequestException, ModbusClientException, ModbusConfigurationException, ModbusDecoderException
from . import requests
from .decoder import ModbusPayloadDecoder
from ..connector import Connector

from ...log import logger
from ...models.device import ModbusProperty, ModbusTCPProperty, ModbusReadRequest, ModbusWriteRequest

from pymodbus.constants import Endian

MODBUS_FUNCTION_TO_CODE={
    0x01: "ReadCoils",
    0x02: "ReadDiscreteInput",
    0x03: "ReadHoldingRegister",
    0x04: "ReadInputRegister",
    0x05: "WriteCoil",
    0x06: "WriteRegister",
}


ORDER_CODE = {
    0: Endian.LITTLE,
    1: Endian.BIG,  
}

class AsyncModbusConnector(Connector):
    def __init__(self, conn_parm:dict):
        self.conn_parm:dict = conn_parm
        self.client: ModbusClient.ModbusBaseClient|None = None
        self._running = False

    async def open(self):
        if self._running:
            return
        comm_str:str = self.conn_parm.get("connectionOption")
        comm = comm_str.lower()
        if comm == "tcp":
            conn_parm = ModbusTCPProperty(**self.conn_parm) 
            self.client = ModbusClient.AsyncModbusTcpClient(
                host=conn_parm.host, 
                port=conn_parm.port,
                framer=FramerType.SOCKET,
                retries=2,
                timeout=1,
            )
        elif comm == "serialport":
            conn_parm = ModbusProperty(**self.conn_parm)
            self.client = ModbusClient.AsyncModbusSerialClient(
                port=conn_parm.port,
                framer=FramerType.RTU,
                baudrate= conn_parm.baudrate,
                bytesize= conn_parm.bytesize,
                parity= conn_parm.parity,
                stopbits= conn_parm.stopbits,
                retries=2,
                timeout=1,
            )
        else:
            raise ValueError(f"modbus unsupport: {comm}")

        await self.client.connect()
        assert self.client.connected

        self._running = True

    
    def close(self):
        if self.client:
            self.client.close()
            self._running = False

    async def read_coils(self, slave:int, requests:list[ModbusReadRequest]):
        rsp = []
        groups = self._merge_requests(requests)
        for group in groups:
            try:
                rr = await self.client.read_coils(
                    address=group["start"], 
                    count=group["end"]+ 1 - group["start"], 
                    slave=slave
                )
            except Exception as err:
                logger.error(f"slave {slave} read_coils error: {err}")
                raise ModbusRequestException(f"modbus {slave} error: {err}")
            
            if rr.isError():
                err_msg = self._get_error_message(rr, group)
                logger.error(err_msg)
                continue
                
            logger.info(f"rr.bits={rr.bits}")
            decoded_meterics:list = self._decoded_bits_for_group(group, rr.bits)
            rsp.extend(decoded_meterics)
            
        return rsp
        
        
    async def read_discrete_inputs(self, slave:int, requests:list[ModbusReadRequest]):
        rsp = []
        groups = self._merge_requests(requests)
        for group in groups:
            try:
                rr = await self.client.read_discrete_inputs(
                    address=group["start"], 
                    count=group["end"]+ 1 - group["start"], 
                    slave=slave
                )
            except Exception as err:
                logger.error(f"slave {slave} read_coils error: {err}")
                raise ModbusRequestException(f"modbus {slave} error: {err}")
            
            if rr.isError():
                err_msg = self._get_error_message(rr, group)
                logger.error(err_msg)
                continue
                
            logger.info(f"rr.bits={rr.bits}")
            decoded_meterics:list = self._decoded_bits_for_group(group, rr.bits)
            rsp.extend(decoded_meterics)
            
        return rsp
        

    async def read_holding_registers(self, slave:int, requests:list[ModbusReadRequest]):
        rsp = []
        groups = self._merge_requests(requests)
        for group in groups:
            
            try:
                rr = await self.client.read_holding_registers(
                    address=group["start"], 
                    count=group["end"]+ 1 - group["start"], 
                    slave=slave
                )
            except Exception as err:
                logger.error(f"slave {slave} read_holding_registers error: {err}")
                raise ModbusRequestException(f"modbus {slave} error: {err}")
            
            if rr.isError():
                err_msg = self._get_error_message(rr, group)
                logger.error(err_msg)
                continue
                
            # logger.debug(f"rr.registers={rr.registers}")
            decoded_meterics:list = self._decoded_registers_for_group(group, rr.registers)
            rsp.extend(decoded_meterics)
            
        return rsp
    
        
    async def read_input_registers(self, slave:int, requests:list[ModbusReadRequest]):
        rsp = []
        groups = self._merge_requests(requests)
        for group in groups:
            
            try:
                rr = await self.client.read_input_registers(
                    address=group["start"], 
                    count=group["end"]+ 1 - group["start"], 
                    slave=slave
                )
            except Exception as err:
                logger.error(f"slave {slave} read_holding_registers error: {err}")
                raise ModbusRequestException(f"modbus {slave} error: {err}")
            
            if rr.isError():
                err_msg = self._get_error_message(rr, group)
                logger.error(err_msg)
                continue
                
            # logger.info(f"rr.registers={rr.registers}")
            decoded_meterics:list = self._decoded_registers_for_group(group, rr.registers)
            rsp.extend(decoded_meterics)
            
        return rsp


    async def write_coil(self, slave:int, request:ModbusWriteRequest):
        try:
            _request = await self.client.write_coil(
                address=request.address, 
                value=request.value, 
                slave=slave
            )

            if _request.isError():
                raise ModbusRequestException(self._get_error_message(_request, request))
            
            return True
        
        except ModbusException as err:
            raise ModbusClientException(f"Could not connect to modbus client : {err}")
        except TimeoutError as err:
            raise ModbusRequestException(f"Request to the modbus device timeout : {err}")
        except Exception as err:
            raise ModbusRequestException(f"Request to the modbus device failed: {err}")


    async def write_register(self, slave:int, request:ModbusWriteRequest):
        try:
            value = request.value
            if request.data_type not in ["str", "string"] and request.divisor > 1:
                value = int(value * request.divisor)

            _response = await self.client.write_register(
                address=request.address, 
                value=value, 
                slave=slave
            )
            if _response.isError():
                raise ModbusRequestException(self._get_error_message(_response, request))
            
            return True
        
        except ModbusException as err:
            raise ModbusClientException(f"Could not connect to modbus client : {err}")
        except TimeoutError as err:
            raise ModbusRequestException(f"Request to the modbus device timeout : {err}")
        except Exception as err:
            raise ModbusRequestException(f"Request to the modbus device failed: {err}") 

    def _get_error_message(self, exception, request, **kwargs) -> str:
        try:
            error_message = f"Error when executing Modbus Request from {self.__class__.__name__} with request {request} : {exception}"
            return error_message
        except Exception as err:
            logger.error(f"Could not generate error msg : {err}")
            return f"Modbus Request failed - Cannot get Error Message : {err}"

    def _decoded_registers_for_group(self, metrics_group:dict, registers:list):
        rsp = []
        for metric in metrics_group['metrics']:
            # req = ModbusReadRequest(**metric)
            req:ModbusReadRequest = metric
            offset = req.address - metrics_group["start"]
            register = registers[offset: offset+req.count]
            
            register_decoded = ModbusPayloadDecoder.decode(
                registers= register, 
                data_type= req.data_type,
                byteorder = ORDER_CODE.get(req.byteorder), 
                wordorder = ORDER_CODE.get(req.wordorder),
                divisor = req.divisor
            )
            rsp.append(
                {
                    "address": req.address,
                    "value": register_decoded
                }
            )
        return rsp
    
    def _decoded_bits_for_group(self, metrics_group:dict, bits:list):
        rsp = []
        for metric in metrics_group['metrics']:
            # req = ModbusReadRequest(**metric)
            req:ModbusReadRequest = metric
            offset = req.address - metrics_group["start"]
            bit = bits[offset]
            rsp.append(
                {
                    "address": req.address,
                    "value": int(bit)
                }
            )
        return rsp


    def _merge_requests(self, requests:list[ModbusReadRequest]):
        # sorted b reg address
        # print("_merge_requests requests=",requests)
        sorted_reqs = sorted(requests, key=lambda x: x.address)
        groups = []
        current_group = None
        for req in sorted_reqs:
            if not current_group:
                # 第一组初始化
                current_group = {
                    'start': req.address,
                    'end': req.address + req.count - 1,
                    'metrics': [req]
                }
            else:
                if req.address == current_group['end'] + 1:
                    # 扩展当前组
                    current_group['end'] = req.address + req.count - 1
                    current_group['metrics'].append(req)
                else:
                    # 保存当前组并创建新组
                    groups.append(current_group)
                    current_group = {
                        'start': req.address,
                        'end': req.address + req.count - 1,
                        'metrics': [req]
                    }
        
        if current_group:
            groups.append(current_group)
        
        return groups


