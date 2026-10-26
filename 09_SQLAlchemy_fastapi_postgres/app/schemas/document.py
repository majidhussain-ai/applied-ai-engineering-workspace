import uuid
from datetime import datetime 
from typing import Annotated, Any
from pydantic import BaseModel, ConfigDict, Field

class DocumentChunkBase(BaseModel):
    chunk_index: Annotated[int, Field(..., ge=0)]
    content: Annotated[str, Field(..., min_length=1)]
    chunk_metadata: Annotated[dict[str, Any], Field(default_factory=dict)]

# RAG will create embedding by matching this validation 
class DocumentChunkCreate(DocumentChunkBase):
    embedding: Annotated[list[float], Field(..., min_length=1536, max_length=1536)]

class DocumentChunkRead(DocumentChunkBase):
    id: uuid.UUID
    document_id: uuid.UUID
    created_at: datetime 

    model_config = ConfigDict(from_attributes=True)

class DocumentBase(BaseModel):
    title: Annotated[str, Field(..., max_length=500)]
    file_path: Annotated[str, Field(..., max_length=500)]
    file_hash: Annotated[str, Field(...,min_length=64, max_length=64)]
    doc_metadata: Annotated[dict[str, Any], Field(default_factory=dict)]

class DocumentCreate(DocumentBase):
    pass 

class DocumentRead(DocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime 
    updated_at: datetime
    chunks: list[DocumentChunkRead] = []

    model_config = ConfigDict(from_attributes=True)

class ScoredChunkRead(DocumentChunkRead):
    distance: Annotated[float, Field(..., description='Cosine Distance Lower is better')]
    similarity_score: Annotated[float, Field(..., description='cosine similarity (1 - cosine_distance) higher is better')]