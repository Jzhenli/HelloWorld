from ..setting import sched_path

class Settings():
    job_store_url: str = f"sqlite:///{sched_path}"

settings = Settings()
