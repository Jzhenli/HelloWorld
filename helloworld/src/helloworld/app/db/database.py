from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from .. setting import app_db_path

db_url = f"sqlite+aiosqlite:///{app_db_path}"

async_engine = create_async_engine(db_url, echo=False)


async_session_maker = async_sessionmaker( 
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session: 
        yield session


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)