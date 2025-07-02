import logging

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from .exceptions import ModbusDecoderException

class ModbusPayloadDecoder:

    _functions_map = {
        "int8": BinaryPayloadDecoder.decode_8bit_int,
        "int16": BinaryPayloadDecoder.decode_16bit_int,
        "int32":BinaryPayloadDecoder.decode_32bit_int,
        "int64": BinaryPayloadDecoder.decode_64bit_int,
        "uint8": BinaryPayloadDecoder.decode_8bit_uint,
        "uint16": BinaryPayloadDecoder.decode_16bit_uint,
        "uint32": BinaryPayloadDecoder.decode_32bit_uint,
        "uint64": BinaryPayloadDecoder.decode_64bit_uint,
        "float16": BinaryPayloadDecoder.decode_16bit_float,
        "float32": BinaryPayloadDecoder.decode_32bit_float,
        "float64": BinaryPayloadDecoder.decode_64bit_float,
        "str": BinaryPayloadDecoder.decode_string,
        "string": BinaryPayloadDecoder.decode_string
    }
    @classmethod
    def decode(cls, registers, data_type, byteorder=Endian.BIG, wordorder=Endian.BIG, divisor:int=1):
        if data_type not in cls._functions_map:
            return registers
        
        try:
            decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=byteorder, wordorder=wordorder)
            f = cls._functions_map[data_type]
            if data_type == "str" or data_type=="string":
                size = len(registers)*2 # one register (word) store 2 char
                return f(decoder, size).decode().strip("\x00")
            
            value = f(decoder)
            if data_type not in ["str", "string"]:
                # decimal_places = len(str(divisor)) - 1
                divisor_str = str(divisor)
                if "." in divisor_str:
                    parts = divisor_str.split('.')
                    decimal_places = len(parts[1].rstrip('0'))
                    print("req.divisor=", divisor, type(divisor), decimal_places)
                    value = f"{value*divisor:.{decimal_places}f}"
                else:
                    value = f"{value*divisor}"
            return value
        except KeyError as err:
            logging.error(f"Encoding specified for decoding isn't valid : {err}.")
            raise ModbusDecoderException(f"Invalid Enconding {data_type}")
        
        except Exception as err:
            logging.error(f"Cannot decode modbus registers : {err}")
            raise ModbusDecoderException(f"Cannot decode values for encoding : {data_type} : {err}")
