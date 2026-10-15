CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE rag_documents CASCADE;

-- __________________ TABLE CREATED FOR ROUGH PRACTICE________________
CREATE TABLE IF NOT EXISTS rag_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_name TEXT NOT NULL,
    content TEXT NOT NULL,           -- The actual chunk of text
    embedding vector(128)            -- Dense Vector (google-genai) 
);

select * from rag_documents;

-- __________________CREATED INDEXED TO VECTORS with hnsw_____________
SET shared_buffers = '1GB';
SET maintenance_work_mem = '1GB';

CREATE INDEX IF NOT EXISTS rag_documents_hnsw_idx
ON rag_documents 
USING HNSW (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- __________________ CREATE INDEX ON VECTORS WITH IVFFlat________________
CREATE INDEX IF NOT EXISTS rag_documents_ifflat_idx ON rag_documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);


-- _______________ FOR PRACTICE CREATE COMPLETE NUMBERS OF VECTORR__________
-- creating pure vectors numbers and make practice on that with others numbers
CREATE TABLE vectors(
    id SERIAL PRIMARY KEY,
    embedding vector(5)
);

