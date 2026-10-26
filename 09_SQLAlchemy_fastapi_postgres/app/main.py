
from contextlib import asynccontextmanager
from fastapi import FastAPI , status
from sqlalchemy import text

from app.api.v1 import v1_router

import app.models
from app.database import Base, DB_Session, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    title= 'AI RAG Backends',
    version= '1.0.0',
    lifespan=lifespan,
    )


app.include_router(v1_router)

@app.get('/health', status_code=status.HTTP_200_OK)
async def health_check(db: DB_Session):
    result = await db.execute(text('SELECT 1'))
    registered_tables = list(Base.metadata.tables.keys())
    return{
        'status' : 'ok',
        'db_ping' : result.scalar_one(),
        'registered_orm_tables' : registered_tables,
    }
