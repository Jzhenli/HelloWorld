import time
import os
import uvicorn
import threading

# def run_uviron():
#     while not (app_env := os.getenv("APP_ENV", None)):
#         time.sleep(0.1)
#         print("Waitting for APP_ENV ....")

#     print("APP_ENV is ready.")
#     from .web import setup_app
#     from ..setting import frontpath
#     uvicorn.run(app=setup_app(frontpath), host="0.0.0.0", port=int(os.getenv("PORT", 9090)))
#     # uvicorn.run(app=setup_app(), host="0.0.0.0", port=int(os.getenv("PORT", 9090)))

def start_uvicorn():
    from .web import setup_app
    from ..setting import frontpath, port
    uvicorn.run(app=setup_app(frontpath), host="0.0.0.0", port=port)



def foreground_cmd_app():
    start_uvicorn()


def background_cmd_app():
    def wait_and_run_uvicron():
        while not (app_env := os.getenv("APP_ENV", None)):
            time.sleep(0.1)
            print("Waitting for APP_ENV ....")

        start_uvicorn()
        
    fastapi_thread = threading.Thread(target=wait_and_run_uvicron, daemon=True)
    fastapi_thread.start()