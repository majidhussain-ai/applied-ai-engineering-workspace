import uuid
import hashlib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate 

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    user_db = User(
        username = user_in.username,
        email = user_in.email,
        hashed_password = hash_password(user_in.password),
    )

    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)
    return user_db












