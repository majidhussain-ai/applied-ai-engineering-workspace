import uuid
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, EmailStr

# Base field common accross schemas
class UserBase(BaseModel):
    username: Annotated[str, Field(..., min_length=3, max_length=30)]
    email: EmailStr

# during user creation profile 
class UserCreate(UserBase):
    password: Annotated[str, Field(..., min_length=8, max_length=30)]

# user can see their data 
class UserRead(UserBase):
    id: uuid.UUID
    is_active: Annotated[bool, Field(default=True)]
    created_at: datetime 
    updated_at: datetime

    # allowing sqlalchemy orm to convert pydantic v2 readable and serialize to validate 
    model_config = ConfigDict(from_attributes=True)

