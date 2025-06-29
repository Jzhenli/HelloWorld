# from fastapi import APIRouter, Request, status
# from .utils import get_logger
# from .schemas import Job

# logger = get_logger()


# class JobNotFoundError(Exception):
#     pass


# def get_jobs_router() -> APIRouter:
#     """Generate a router with the scheduler routes."""
#     router = APIRouter()
#     @router.post("", name="scheduler:add_job", status_code=status.HTTP_201_CREATED)
#     async def add_job(request: Request, job: Job):
#         logger.debug(f"job.id={job.id}")
#         job_dict = job.dict()  #此处为了兼容pydantic V1
#         # param_dict["kwargs"]={"device_id":param_dict["id"]}
#         job = request.app.state.scheduler.add_job(**job_dict)
#         return {"job": f"{job.id}"}

#     @router.get("", name="scheduler:get_jobs", response_model=list)
#     async def get_jobs(request: Request):
#         jobs = request.app.state.scheduler.get_jobs()
#         jobs = [{k: v for k, v in job.__getstate__().items() if k != "trigger"} for job in jobs]
#         return jobs

#     @router.delete("/{job_id}", name="scheduler:remove_job")
#     async def remove_job(request: Request, job_id: str):
#         try:
#             deleted = request.app.state.scheduler.remove_job(job_id=job_id)
#             logger.debug(f"Job {job_id} deleted: {deleted}")
#             return {"job": f"{job_id}"}
#         except AttributeError as err:
#             raise JobNotFoundError(f"No job by the id of {job_id} was found") from err

#     return router

# from .scheduler import get_scheduler
# async def init_job():
#     scheduler = get_scheduler()
#     polling_job = {
#         "func": "xplay.app.task:polling_job",
#         "trigger": "interval",
#         "seconds": 3,
#         "id": "polling_job",
#         "kwargs": {}
#     }

#     monitor_db = {
#         "func": "xplay.app.task:monitor_db",
#         "trigger": "interval",
#         "seconds": 300,
#         "id": "monitor_db",
#         "kwargs": {}
#     }
#     scheduler.add_job(**polling_job)
#     scheduler.add_job(**monitor_db)