import uuid
from sqlalchemy import select
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentChunkCreate, DocumentCreate


async def create_document_with_chunks(
    session: AsyncSession,
    user_id: uuid.UUID,
    doc_in: DocumentCreate,
    chunks_in: list[DocumentChunkCreate],
) -> Document:
    # 1. Parent Document initiate karein
    db_document = Document(
        user_id=user_id,
        title=doc_in.title,
        file_path=doc_in.file_path,
        file_hash=doc_in.file_hash,
        doc_metadata=doc_in.doc_metadata,
    )
    session.add(db_document)
    await session.flush()  # DB se Document ID generate karwata hai bina transaction commit kiye

    # 2. Child Chunks ko parent Document ID se attach karein
    db_chunks = [
        DocumentChunk(
            document_id=db_document.id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            embedding=chunk.embedding,
            chunk_metadata=chunk.chunk_metadata,
        )
        for chunk in chunks_in
    ]
    session.add_all(db_chunks)

    # 3. Dono operations ko atomically commit karein
    await session.commit()

    # 4. Eager-load chunks taake Pydantic schema serialize kar sake
    document = await get_document_by_id(session, db_document.id)
    assert document is not None
    return document


async def get_document_by_id(
    session: AsyncSession,
    document_id: uuid.UUID,
) -> Document | None:
    statement = (
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.chunks))  # Async relationship loading
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def search_similar_chunks(
    session: AsyncSession,
    query_vector: list[float],
    limit: int = 5,
    max_distance: float = 0.55,
    document_id: uuid.UUID | None = None,
    metadata_filter: dict[str, Any] | None = None,
) -> list[tuple[DocumentChunk, float]]:

    """
    Performs HNSW cosine similarity search with a strict distance threshold,
    returning tuples of (DocumentChunk, cosine_distance).
    """
    distance_expr = DocumentChunk.embedding.cosine_distance(query_vector).label('distance')
    
    statement = select(DocumentChunk, distance_expr).where(distance_expr <= max_distance)

    if document_id is not None:
        statement = statement.where(DocumentChunk.document_id == document_id)

    if metadata_filter:
        statement = statement.where(
            DocumentChunk.chunk_metadata.contains(metadata_filter)
        )

    statement = statement.order_by(distance_expr).limit(limit)

    result = await session.execute(statement)
    return [(row[0] , float(row[1])) for row in result.all()]  

