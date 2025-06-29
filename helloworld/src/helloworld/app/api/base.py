from fastapi import APIRouter
from ..setting import frontpath
router = APIRouter(prefix="/iot",tags=["base"])

@router.get("/health")
def check_online():
    return {"status": "OK"}


@router.get("/version")
def get_version():
    from xplay import __version__
    xplay_ver = __version__
    
    try:
        ui_version = frontpath.joinpath("version.txt")
        with open(ui_version, 'r', encoding='utf-8') as file:
            content  = file.readline().strip()
        if ':' in content :
            _, ui_ver = content.split(':', 1) 
        else:
            ui_ver = "unknown"
    except FileNotFoundError:
        ui_ver = "unknown"

    version ={
        "Version":xplay_ver,
        "info":{
            "xplay_core":xplay_ver,
            "xplay_ui":ui_ver,
        }
    }
    return version

@router.get("/login")
def login():
    return {"status": "OK"}