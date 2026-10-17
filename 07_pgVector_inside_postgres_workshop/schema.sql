CREATE EXTENSION IF NOT EXISTS vector;

TRUNCATE TABLE rag_documents RESTART IDENTITY CASCADE;
DROP TABLE IF EXISTS rag_documents CASCADE;

CREATE TABLE IF NOT EXISTS rag_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL DEFAULT '123e4567-e89b-12d3-a456-426614174000',
    user_name TEXT NOT NULL,
    content TEXT NOT NULL, -- Actual text chunk
    
    -- Automatic generated Full-Text Search column for Sparse/Keyword search
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    embedding vector(128),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Indexes for High-Speed Hybrid Search
-- HNSW Index for Dense Vector Similarity
CREATE INDEX IF NOT EXISTS rag_documents_hnsw_idx
ON rag_documents 
USING HNSW (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- GIN Index for Sparse Full-Text Keyword Search
CREATE INDEX IF NOT EXISTS rag_documents_gin_idx 
ON rag_documents 
USING GIN (search_vector);