-- 8 Sample Rows with valid 738-dimension float arrays converted to vectors
INSERT INTO rag_documents (user_name, content, embedding) VALUES

-- Row 1: About Vector Search
('majidhussain-ai','Retrieval-Augmented Generation (RAG) blends dense vector retrieval
with LLMs to mitigate generation hallucinations.', NULL),

-- Row 2: About Indexing
('amjadhussain-ai','HNSW indexes with ID sk-u4sink and PRODUCT WITH amazon product ID-IPHONE13 PRO WITH ID  construct multi-layered graphs providing low latency queries even across
millions of dense array data points.', NULL), 

-- Row 3: About Microservices
('amirkhan_ai','Microservice architectures ERR-504-GATEWAY-TIMEOUT frequently encapsulate localized context
data chunks communicating over highly typed gRPC contracts with texting codes E11.9.', NULL),

-- Row 4: About Quantization
('yasirkhan_ai','Scalar and Binary Quantization compress high-dimension components to drastically
minimize RAM constraints under heavy load.', NULL), 


-- Row 5: About LLM Context Windows
('ayankhan_ai','Context windows dictate the hard absolute threshold of raw tokens an attention
mechanism can ingest in a single pass.', NULL),

-- Row 6: About Hybrid Search
('jaleelkhan_ai','Combining traditional relational inverted BM25 text indices alongside proximity
vectors yields maximum context relevance scores with model v3.0.5-beta.', NUll),

-- Row 7: About Database Sharding
('saqlainkhan_ai','Sharding relational datasets across physical instances separates execution compute
paths allowing massive write patterns horizontally.', NULL),
-- Row 8: About Cache Pre-warming
('tahirkhan_ai','Pre-warming cache infrastructures via selective index hydration blocks premature
cold-start latency vectors impacting production users.', NULL);


INSERT INTO vectors (embedding) VALUES ('[1,2,3,4,2]') , ('[3,2,1,4,1]') , ('[8,9,5,7,5]'), ('[8,7,6,5,5]');

SELECT * FROM vectors;