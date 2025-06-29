from .scheduler import get_scheduler

async def init_job():
    scheduler = get_scheduler()
    jobs = scheduler.get_jobs()
    jobs_list = [job.id for job in jobs]
    print(jobs_list)
    if "polling_device" not in jobs_list:
        polling_job = {
            "func": "xplay.app.task:polling_device",
            "trigger": "interval",
            "seconds": 3,
            "id": "polling_device",
            "kwargs": {}
        }
        scheduler.add_job(**polling_job)

    if "monitor_db" not in jobs_list:
        monitor_db = {
            "func": "xplay.app.task:monitor_db",
            "trigger": "interval",
            "seconds": 300,
            "id": "monitor_db",
            "kwargs": {}
        }
        scheduler.add_job(**monitor_db)