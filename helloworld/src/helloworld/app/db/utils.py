from .models import Device, Point, Metric
from .database import async_session_maker
from ..log import logger
from sqlmodel import select, delete, func
from sqlalchemy.orm import load_only


async def get_all_devices():
    async with async_session_maker() as session:
        result = await session.execute(select(Device))
        devices = result.scalars().all()
        return list(devices)


async def get_metrics_by_device(device_id):
    async with async_session_maker() as session:
        result = await session.execute(select(Metric).where(Metric.device_id==device_id))
        metrics = result.scalars().all()
        return list(metrics)

async def set_points(points):
    async with async_session_maker() as session:
        db_points = [Point.model_validate(point) for point in points]
        session.add_all(db_points)
        await session.commit()
   

async def trim_points_for_metric(max_points: int = 100):
    """
    Asynchronously trims the number of points for each metric_id, keeping only the most recent `max_points`.
    """
    async with async_session_maker() as session:
        try:
            metric_ids = await session.scalars(select(Metric.id))
            for metric_id in metric_ids.all():  
                subquery = (
                    select(Point.timestamp)
                    .where(Point.metric_id == metric_id)
                    .order_by(Point.timestamp.desc())
                    .offset(max_points - 1)
                    .limit(1)
                    .scalar_subquery()
                )

                delete_stmt = (
                    delete(Point)
                    .where(Point.metric_id == metric_id)
                    .where(Point.timestamp < subquery)
                )

                result = await session.execute(delete_stmt)
                deleted_count = result.rowcount
                
                if deleted_count > 0:
                    logger.info(f"Metric {metric_id}: delete {deleted_count} old points.")

            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"trim_points_for_metric: {str(e)}")
