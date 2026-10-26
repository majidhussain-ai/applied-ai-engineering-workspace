from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import UUIDPrimaryKeyMixin, TimestampMixin
if TYPE_CHECKING:
    from app.models.document import Document

"""
class User():
    -username
    -email
    -hashed_password
    -is_active
    -documents
"""


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'users'
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    documents: Mapped[list[Document]] = relationship(
        back_populates = 'owner',
        cascade = 'all, delete-orphan',
        passive_deletes = True,
    )