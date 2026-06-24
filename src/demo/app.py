"""FastAPI Application"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(title="demo")


def get_resource_dir() -> Path:
    mod = sys.modules.get("demo")
    if mod and hasattr(mod, "_RESOURCE_DIR"):
        return Path(mod._RESOURCE_DIR) / "resources"
    return Path(__file__).parent / "resources"


RESOURCES_DIR = get_resource_dir()
STATIC_DIR = RESOURCES_DIR / "static"
IS_DEV_MODE = os.environ.get("APP_MODE", "production") == "dev"

FRONTEND_AVAILABLE = STATIC_DIR.exists() and any(STATIC_DIR.iterdir())
if FRONTEND_AVAILABLE:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
elif not IS_DEV_MODE:
    print(f"Warning: Frontend not found at {STATIC_DIR}")


@app.get("/")
async def index():
    if FRONTEND_AVAILABLE:
        return FileResponse(STATIC_DIR / "index.html")
    return JSONResponse({
        "message": "Frontend not available",
        "mode": "development" if IS_DEV_MODE else "production",
        "hints": ["cd frontend && npm run dev", "npm run build && pyapp build <platform>", "/docs"]
    })


@app.get("/api/health")
async def health():
    return { "status": "ok", "frontend": "available" if FRONTEND_AVAILABLE else "not_built" }


@app.post("/api/restart")
async def restart():
    import signal, threading
    def _restart():
        sig = signal.SIGINT if sys.platform == "win32" else signal.SIGTERM
        os.kill(os.getpid(), sig)
    threading.Timer(0.5, _restart).start()
    return { "status": "restarting" }


def main():
    import uvicorn
    port = int(os.environ.get("APP_PORT", "18080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
