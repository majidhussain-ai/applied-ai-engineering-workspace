import uuid
from fastapi import APIRouter, status, HTTPException

from app.schemas.user import UserCreate, UserRead
from app.database import DB_Session
from app.crud.user import get_user_by_email, get_user_by_id, create_user

router = APIRouter(prefix='/users', tags=['User'] )

@router.post('/', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: DB_Session):
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='A user with this email is already exists',
        )
    return await create_user(db, user_in)

@router.get('/{user_id}', response_model=UserRead)
async def user_read(user_id: uuid.UUID, db: DB_Session):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='user not found',
        )
    return user 
