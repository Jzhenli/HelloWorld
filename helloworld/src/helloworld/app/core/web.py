from typing import Optional
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_offline import FastAPIOffline as FastAPI
from ..db.database import create_db_and_tables
from ..sched import get_scheduler, init_job
from ..api import router
from ..device import device_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.scheduler = get_scheduler()
    try:
        await create_db_and_tables()
        await device_manager.start()
        app.state.scheduler.start()
        # await init_job()
        yield
    finally:
        app.state.scheduler.shutdown()


def create_app():
    """Create the FastAPI app and include the router."""

    app = FastAPI(title="IoT Gateway API", lifespan=lifespan)
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(router)
    # app.include_router(get_jobs_router(), prefix="/scheduler", tags=["scheduler"])
    
    return app


def setup_static_files(app: FastAPI, static_files_dir):
    """
    Setup the static files directory.
    Args:
        app (FastAPI): FastAPI app.
        path (str): Path to the static files directory.
    """
    app.mount(
        "/",
        StaticFiles(directory=static_files_dir, html=True),
        name="static",
    )

def setup_app(frontpath:Optional[Path]=None) -> FastAPI:
    app = create_app()
    if frontpath and frontpath.exists():
        setup_static_files(app, frontpath)
    return app