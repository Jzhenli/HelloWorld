"""Modbus Requests
This module defines all requests that can be made with modbus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pymodbus.constants import Endian


@dataclass
class ReadCoils:
    address: int
    count: int = field(default=1)
    unit: int = field(default=1)


@dataclass
class WriteCoils:
    address: int
    values: list
    unit: int = field(default=1)


@dataclass
class ReadDiscreteInput:
    address: int
    count: int = field(default=1)
    unit: int = field(default=1)


@dataclass
class ReadHoldingRegister:
    address: int
    count: int = field(default=1)
    slave: int = field(default=1)
    data_type: str = field(default="int16")
    byteorder: Endian = field(default=Endian.BIG)
    wordorder: Endian = field(default=Endian.BIG)


@dataclass
class ReadInputRegister:
    address: int
    count: int = field(default=1)
    unit: int = field(default=1)
    # encoding: str = field(default="bool")


@dataclass
class WriteRegister:
    address: int
    values: list
    unit: int = field(default=1)
