from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size = settings.DB_POOL_SIZE,
    max_overflow = settings.DB_MAX_OVERFLOW,
    echo = settings.DB_ECHO,
    pool_pre_ping = True,
    pool_recycle = 1800,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

# per session request management dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise 

DB_Session = Annotated[AsyncSession, Depends(get_db)]
