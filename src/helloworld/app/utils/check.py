
prefixes = (
    "StartStopCommand",
    "StartStopStatus",
    "TempAdjust",
    "RoomTemp",
    "AirConModeCommand",
    "AirConModeStatus",
    "AirFlowRateCommand",
    "AirFlowRateStatus",
    "AirDirectionCommand",
    "AirDirectionStatus",
    "RemoteControlStart",
    "RemoteControlAirConModeSet",
    "RemoteControlTempAdjust",
    "Alarm",
    "MalfunctionCode",
    "CommunicationStatus",
    "CompressorStatus",
    "FilterSign",
    "FilterSignReset",
    "CompressorStatus"
)

def starts_with_any_prefix(s:str):
    return s.startswith(prefixes)

