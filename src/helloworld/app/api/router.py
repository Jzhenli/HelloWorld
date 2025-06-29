from .base import router as base_api
from .v1.sched import router as sched_api
from .v1.device import router as device_api
from .v1.metric import router as metric_api
from .v1.point import router as point_api
from .v1.action import router as action_api
from .v1.project import router as project_api
from fastapi import APIRouter

router = APIRouter()

router.include_router(base_api)
router.include_router(device_api)
router.include_router(metric_api)
router.include_router(point_api)
router.include_router(action_api)
router.include_router(sched_api)
router.include_router(project_api)


