import hashlib
import uuid
from typing import Any, Annotated
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.crud.document import (
    create_document_with_chunks,
    get_document_by_id,
    search_similar_chunks,
)
from app.crud.user import get_user_by_id
from app.database import DB_Session
from app.schemas.document import (
    DocumentChunkCreate,
    DocumentChunkRead,
    DocumentCreate,
    DocumentRead,
    ScoredChunkRead,
)
from app.services.rag_service import (
    chunk_extracted_pages,
    extract_text_from_file,
    generate_document_embeddings,
    generate_query_embedding,
    generate_rag_answer,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


# ==========================================
# Request / Response Schemas for Endpoints
# ==========================================

class DocumentIngestRequest(BaseModel):
    user_id: uuid.UUID
    document: DocumentCreate
    chunks: list[DocumentChunkCreate] = Field(..., min_length=1)


class SemanticSearchRequest(BaseModel):
    query_vector: list[float] = Field(..., min_length=1536, max_length=1536)
    limit: int = Field(default=5, ge=1, le=20)
    document_id: uuid.UUID
    max_distance: Annotated[float, Field(default=0.55, ge=0.0, le=2.0)]
    metadata_filter: dict[str, Any] | None = None

# NEW: Request schema for real-time RAG Question-Answering
class RAGQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    top_k: int = Field(default=4, ge=1, le=10)
    document_id: Annotated[
        uuid.UUID | None , Field(
            default=None,
            examples=[None],
            description="Optional: Restrict search to a specific uploaded document UUID",
        )]
    max_distance: Annotated[float, Field(default=0.55, ge=0.0, le=2.0, description='maximum cosine distance threshold drop irrelevant docs')]

    metadata_filter: Annotated[
        dict[str, Any] | None ,
        Field(
            default=None,
            examples=[None],
            description= "Optional JSONB filter, e.g. {'page_number': 1} or {'source': 'sample.pdf'}",
        )]


# NEW: Response schema showing AI Answer + Retrieved Source Chunks
class RAGQueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[ScoredChunkRead]


# ==========================================
# Existing Endpoints
# ==========================================

@router.post("/", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def ingest_document(payload: DocumentIngestRequest, db: DB_Session):
    user = await get_user_by_id(db, payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner user does not exist.",
        )

    return await create_document_with_chunks(
        session=db,
        user_id=payload.user_id,
        doc_in=payload.document,
        chunks_in=payload.chunks,
    )


@router.get("/{document_id}", response_model=DocumentRead)
async def read_document(document_id: uuid.UUID, db: DB_Session):
    document = await get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    return document


@router.post("/search", response_model=list[ScoredChunkRead])
async def search_chunks(payload: SemanticSearchRequest, db: DB_Session):
    rows =  await search_similar_chunks(
        session=db,
        query_vector=payload.query_vector,
        limit=payload.limit,
        document_id=payload.document_id,
        metadata_filter=payload.metadata_filter,
        max_distance= payload.max_distance
    ) 

    return [ScoredChunkRead(
        **DocumentChunkRead.model_validate(chunk).model_dump(),
        distance=round(dist, 4),
        similarity_score = round(1.0 - dist, 4),
    )
    for chunk, dist in rows
    ]

# ==========================================
# NEW: Step 11 Real-Time Upload & RAG Endpoints
# ==========================================

@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_and_ingest_file(
    db: DB_Session,
    user_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
):
    # 1. Verify User Exists
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner user does not exist.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename.",
        )

    # 2. Read raw file bytes & compute SHA-256 hash
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    # 3. Extract text from PDF/TXT & split into overlapping chunks
    try:
        pages = extract_text_from_file(file_bytes, file.filename)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err

    if not pages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract any readable text from the file.",
        )

    raw_chunks = chunk_extracted_pages(pages, chunk_size=800, chunk_overlap=150)

    # 4. Generate Real 1536-dim Embeddings via Gemini API
    chunk_texts = [c["content"] for c in raw_chunks]
    embeddings = await generate_document_embeddings(chunk_texts)

    # 5. Prepare Pydantic Data Contracts for DB Insertion
    doc_in = DocumentCreate(
        title=file.filename,
        file_path=f"/uploads/{file.filename}",
        file_hash=file_hash,
        doc_metadata={
            "filename": file.filename,
            "content_type": file.content_type,
            "total_pages": len(pages),
            "total_chunks": len(raw_chunks),
        },
    )

    chunks_in = [
        DocumentChunkCreate(
            chunk_index=c["chunk_index"],
            content=c["content"],
            embedding=emb,
            chunk_metadata=c["chunk_metadata"],
        )
        for c, emb in zip(raw_chunks, embeddings, strict=True)
    ]

    # 6. Atomically save Document + Chunks in PostgreSQL
    return await create_document_with_chunks(
        session=db,
        user_id=user_id,
        doc_in=doc_in,
        chunks_in=chunks_in,
    )


@router.post("/ask", response_model=RAGQueryResponse)
async def ask_question(payload: RAGQueryRequest, db: DB_Session):
    # 1. Convert user question into 1536-dim query vector via Gemini
    query_vector = await generate_query_embedding(payload.question)

    # 2. Retrieve Top-K closest chunks from PostgreSQL using HNSW Cosine Distance
    scored_rows = await search_similar_chunks(
        session=db,
        query_vector=query_vector,
        limit=payload.top_k,
        document_id=payload.document_id,
        metadata_filter=payload.metadata_filter,
        max_distance= payload.max_distance,

    )

    if not scored_rows:
        return RAGQueryResponse(
            question=payload.question,
            answer="No relevant information found within the similarity threshold.",
            sources=[],
        )

    # 3. Pass retrieved chunk texts + question to Gemini 2.5 Flash
    context_texts = [chunk.content for chunk, _ in scored_rows]
    scored_rows = [ScoredChunkRead(
        **DocumentChunkRead.model_validate(chunk).model_dump(),
        distance= round(dist, 4),
        similarity_score= round(1.0 - dist, 4),

        )
        for chunk, dist in scored_rows
        ]
    

    ai_answer = await generate_rag_answer(
        query=payload.question,
        context_chunks=context_texts,
    )

    # 4. Return AI answer along with exact source chunks used
    return RAGQueryResponse(
        question=payload.question,
        answer=ai_answer,
        sources=scored_rows,
    )

