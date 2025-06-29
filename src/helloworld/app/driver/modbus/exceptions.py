class ModbusRequestException(Exception):
    """ Wrong request parameters """


class ModbusClientException(Exception):
    pass


class ModbusDecoderException(Exception):
    """ Cannot decode the modbus response """


class ModbusConfigurationException(Exception):
    """ Invalid configuration for Modbus Client """