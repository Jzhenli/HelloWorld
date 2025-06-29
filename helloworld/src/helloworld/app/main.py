import platform
import os
from pathlib import Path
from dotenv import load_dotenv

current_path = Path(__file__).resolve()

def cmd_app():
    from .core.server import foreground_cmd_app
    foreground_cmd_app()

def ui_app():
    from .core.gui import foreground_ui_app
    from .core.server import background_cmd_app
    background_cmd_app()
    foreground_ui_app()


def main():
    app_root = current_path.parent.parent
    env_path = app_root.joinpath("resources", ".env")
    print("env_path=", env_path)
    load_dotenv(dotenv_path=env_path)
    console_app = os.getenv("GUI_APP", "True").lower() not in ("true", "1", "yes")
    arch = platform.machine()
    if arch == "armv7l" or console_app:
        cmd_app()
    else:
        ui_app()
