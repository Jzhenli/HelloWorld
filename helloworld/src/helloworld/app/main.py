import platform
from helloworld.app.server import run_server

def main():
    current_os = platform.system()
    if current_os == 'Windows':
        from helloworld.app.client import run_client
        from threading import Thread
        thread = Thread(target=run_server, daemon=True)
        thread.start()
        run_client()
    elif current_os == 'Linux':
        run_server()
    else:
        raise ImportError(f"Unsupported os: {current_os}.")