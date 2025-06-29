from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .config import settings

jobstores = {"default": SQLAlchemyJobStore(url=settings.job_store_url, tablename="jobs")}
scheduler = AsyncIOScheduler(jobstores=jobstores)

def get_scheduler():
    return scheduler