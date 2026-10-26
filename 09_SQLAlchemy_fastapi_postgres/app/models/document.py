from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey,Index,String,Integer,Text, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User

"""
class Document(inherited):
    - user_id fk
    - title
    - file_path
    - file_hash
    - doc_metadata
    - owner
    - chunks

class DocumentChunk(inherited):
    - document_id fk
    - chunk_index
    - content
    - embedding
    - chunk_metadata
    - docuement
"""

class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'documents'
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete = 'CASCADE'),
        index= True,
    )
    title: Mapped[str] = mapped_column(
        String(50),
        index= True,
    )
    file_path: Mapped[str] = mapped_column(String(255))
    file_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    doc_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    # many to one relationship back referece to User 
    owner: Mapped[User] = relationship(back_populates = 'documents')

    # 1 to N (One Document -> Many DocumentChunks)
    chunks: Mapped[list[DocumentChunk]] = relationship(
        back_populates = 'document',
        cascade='all, delete-orphan',
        passive_deletes = True,
        order_by="DocumentChunk.chunk_index",
    )

    __table_args__ = (
        Index(
        'ix_document_metadata_gin',
        'doc_metadata',
        postgresql_using = 'gin',
    ),
    )


class DocumentChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'document_chunks'
    
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('documents.id', ondelete='CASCADE'),
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))
    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    # 1 to N backreference to Document
    document: Mapped[Document] = relationship(back_populates='chunks')
    __table_args__ = (
        Index(
        'ix_document_chunks_embedding_hnsw',
        'embedding',
        postgresql_using = 'hnsw',
        postgresql_with = {'m': 16, 'ef_construction' :64 },
        postgresql_ops = {'embedding' : 'vector_cosine_ops'},
    ),
        Index(
            'ix_document_chunks_metadata_gin',
            'chunk_metadata',
            postgresql_using = 'gin',
        ),
    )
