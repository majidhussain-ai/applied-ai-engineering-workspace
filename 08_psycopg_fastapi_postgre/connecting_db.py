
# from contextlib import asynccontextmanager
# from fastapi import FastAPI , HTTPException, status
# from typing import Optional, List
# from pydantic import BaseModel
# from pgvector.psycopg import register_vector_async
# from psycopg_pool import AsyncConnectionPool
# from psycopg.rows import dict_row, class_row
# import hashlib
# import json

# practice q1 with AsyncConnectionPool for multiple connected pooling at a time

# ________________________1_____________________________
"""
DB_URL = "postgresql://postgres:majid1214@localhost:5432/postgres"
pool: AsyncConnectionPool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    async with AsyncConnectionPool(DB_URL, min_size=1, max_size=10) as db_pool:
        pool = db_pool
        yield

app = FastAPI(lifespan=lifespan)

@app.get('/rag_documents/{user_name}', tags=['Rag Documentation'])
async def get_documents(user_name):
    global pool
    if not pool:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='database is not initialized')

    try:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT user_name, search_vector, content, embedding from rag_documents where user_name = %s;", (user_name,)
                    )
                row = await cur.fetchone()
                if not row:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Docs not found')
                return {
                    'user_name' : row[0],
                    'SearchKeyword' : row[1],
                    'Context' : row[2],
                    'Embedded' : row[3]
                }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""
#_________________________2________________________________

# Practice q2: With Transaction until all operations success , of one fail roolback
"""
DB_URL = "postgresql://postgres:majid1214@localhost:5432/postgres"
pool: AsyncConnectionPool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    async with AsyncConnectionPool(DB_URL, min_size=1, max_size=10) as db_pool:
        pool = db_pool
        yield

app = FastAPI(lifespan=lifespan)

class document_create(BaseModel):
    user_name: str
    content: str

@app.post('/documents', status_code=status.HTTP_201_CREATED)
async def get_documents(doc: document_create):
    global pool
    if not pool:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='database is not initialized')

    try:
        async with pool.connection() as conn:
            async with conn.transaction():
                async with conn.cursor() as cur:
                    await cur.execute(
                        
                        INSERT INTO rag_documents (user_name, content) 
                        VALUES (%s, %s) RETURNING id;
                    
                        (doc.user_name, doc.content)
                        )
                    row = await cur.fetchone()
                    doc_id = row[0]
                    put here and above multi-line string then it will run
                    await cur.execute(
                        
                        INSERT INTO document_audit_logs (document_id, action) 
                        VALUES (%s, 'CREATED');
                        
                        (doc_id,)
                    )
                    
                return {"message": "Document created and audited successfully", "document_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

"""

# Practice q3: register_vector_async used for converting of list of python vectors into database vector format so that we easily insert and fetch vectors from postgres
# __________________________3___________________________
"""
DB_URL = "postgresql://postgres:majid1214@localhost:5432/postgres"
pool: AsyncConnectionPool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    async with AsyncConnectionPool(DB_URL, min_size=1, max_size=10, kwargs = {'row_factory':dict_row}) as db_pool:
        pool = db_pool
        async with pool.connection() as conn:
            await register_vector_async(conn)
        yield

app = FastAPI(lifespan=lifespan)

class DocumentWithEmbedding(BaseModel):
    user_name: str 
    content: str 
    embedding: list[float]

@app.post('/documents/vector', status_code=status.HTTP_201_CREATED)
async def create_vector_document(doc: DocumentWithEmbedding):  
    global pool
    if not pool:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='database pool not initialized')
    
    # 1. Content hashing generate karna
    content_hash = hashlib.sha256(f"{doc.user_name}:{doc.content}:{doc.embedding}".encode('utf-8')).hexdigest()
    
    try:
        async with pool.connection() as conn:
            await register_vector_async(conn)
            async with conn.cursor() as cur:
                # 2. Insert with ON CONFLICT DO NOTHING
                await cur.execute(
                    Write in this line and below triple quetes
                    INSERT INTO rag_documents(user_name, content, embedding, content_hashing)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (content_hashing) DO NOTHING
                    RETURNING user_name;
                    
                    (doc.user_name, doc.content, doc.embedding, content_hash)
                )
                row = await cur.fetchone()
                
                if not row:
                    return {"message": "Document already exists (Duplicate skipped)", "inserted": False}
                    
                return {
                    'user_name': row[0], 
                    'message': 'vector document inserted successfully',
                    'inserted': True
                }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get('/documents/vector/{user_name}', tags=['Rag Documentation'])
async def get_vector_documents(user_name: str):
    global pool
    if not pool:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='database is not initialized')

    try:
        async with pool.connection() as conn:
            await register_vector_async(conn)
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT user_name, search_vector, content, embedding FROM rag_documents WHERE user_name = %s;", 
                    (user_name,)
                )
                row = await cur.fetchone()
                if not row:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Docs not found')
                embedded_list = row['embedding'].to_list() if row['embedding'] is not None else [] 
                return {
                    'user_name': row['user_name'],
                    'SearchKeyword': row['search_vector'],
                    'Context': row['content'],
                    'Embedded': embedded_list[:10]
                }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""
# ______________________________4______________________________________________
# practice q4: cosine similarity search base queries inside fastapi
# from contextlib import asynccontextmanager
# from fastapi import FastAPI , HTTPException, status
# from typing import Any
# from pydantic import BaseModel
# from pgvector.psycopg import register_vector_async
# from psycopg import AsyncConnection
# from psycopg_pool import AsyncConnectionPool
# from psycopg.rows import dict_row



# DB_URL = "postgresql://postgres:majid1214@localhost:5432/postgres"
# pool: AsyncConnectionPool[AsyncConnection[dict[str, Any]]] | None = None

# @asynccontextmanager
# async def lifespan(_app: FastAPI):
#     global pool 
#     _ = _app
#     async def configure(conn: AsyncConnection[dict[str, Any]]) -> None:
#         await register_vector_async(conn)

#     async with AsyncConnectionPool[AsyncConnection[dict[str, Any]]](
#         DB_URL, min_size =1, max_size=10,
#         kwargs = {'row_factory':dict_row},
#         configure = configure
#     ) as db_pool:
        
#         pool = db_pool

#         yield

# app = FastAPI(lifespan=lifespan)

# class SearchQuery(BaseModel):
#     query_embedding: list[float]
#     match_count: int = 5

# @app.post('/documents/search' , tags=['Rag Documents Search'])
# async def search_vector_documents(search: SearchQuery):
#     global pool 
#     if not pool:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail = 'database not initialized')
    
#     try:
#         async with pool.connection() as conn:
#             async with conn.cursor() as cur:
#                 await cur.execute(
#                     """
#                     select user_name, content, search_vector , (embedding <=> %s::vector) as distance
#                     from rag_documents
#                     order by embedding <=> %s::vector 
#                     limit %s;
#                     """, (search.query_embedding, search.query_embedding, search.match_count )
#                 )
#                 rows = await cur.fetchall()
#                 if not rows:
#                     return {'message': 'No matching documents found', 'results':[]}
#                 results = []
#                 for row in rows:
#                     results.append({
#                         'user_name': row['user_name'],
#                         'content': row['content'],
#                         'search_vector' : row['search_vector'],
#                         'similarity_score' : round(1-row['distance'], 3)
#                     })

#                 return {
#                     'total_matches' : len(results),
#                     'results' : results
#                 }
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# ______________________________________5___________________________________________
# practice q5: meta data filtering 
"""When user search anything , our cosine similarity match searched query accross database
    But in real world application just match from database that user who give query of prompt instead of including others users data)"""

# from contextlib import asynccontextmanager
# from fastapi import FastAPI , HTTPException, status
# from typing import Any
# from pydantic import BaseModel, Field
# from pgvector.psycopg import register_vector_async
# from psycopg import AsyncConnection
# from psycopg_pool import AsyncConnectionPool
# from psycopg.rows import dict_row



# DB_URL = "postgresql://postgres:majid1214@localhost:5432/postgres"
# pool: AsyncConnectionPool[AsyncConnection[dict[str, Any]]] | None = None

# @asynccontextmanager
# async def lifespan(_app: FastAPI):
#     global pool 
#     _ = _app
#     async def configure(conn: AsyncConnection[dict[str, Any]]) -> None:
#         await register_vector_async(conn)

#     async with AsyncConnectionPool[AsyncConnection[dict[str, Any]]](
#         DB_URL, min_size =1, max_size=10,
#         kwargs = {'row_factory':dict_row},
#         configure = configure
#     ) as db_pool:
        
#         pool = db_pool

#         yield

# app = FastAPI(lifespan=lifespan)

# class FilteredSearchQuery(BaseModel):
#     query_embedding: list[float]
#     target_user_name: str 
#     match_count: int = Field(default=5, le=10)

# @app.post('/documents/search' , tags=['Rag Documents Search'])
# async def search_vector_documents(search: FilteredSearchQuery):
#     global pool 
#     if not pool:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail = 'database not initialized')
    
#     try:
#         async with pool.connection() as conn:
#             async with conn.cursor() as cur:
#                 await cur.execute(
#                     """
#                     select user_name, content, search_vector , (embedding <=> %s::vector) as distance
#                     from rag_documents
#                     where user_name = %s
#                     order by embedding <=> %s::vector 
#                     limit %s;
#                     """, (search.query_embedding, search.target_user_name, search.query_embedding, search.match_count )
#                 )
#                 rows = await cur.fetchall()
#                 if not rows:
#                     return {'message': 'No matching documents found', 'results':[]}
#                 results = []
#                 for row in rows:
#                     results.append({
#                         'user_name': row['user_name'],
#                         'content': row['content'],
#                         'search_vector' : row['search_vector'],
#                         'similarity_score' : round(1-row['distance'], 3)
#                     })

#                 return {
#                     'filter_applied' : search.target_user_name,
#                     'total_matches' : len(results),
#                     'results' : results
#                 }
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ____________________________6_______________________________________
# Practice Q6. Hybrid search through RRF formula(dense + semantic)


# from contextlib import asynccontextmanager
# from fastapi import FastAPI , HTTPException, status
# from typing import Any
# from pydantic import BaseModel, Field
# from pgvector.psycopg import register_vector_async
# from psycopg import AsyncConnection
# from psycopg_pool import AsyncConnectionPool
# from psycopg.rows import dict_row



# DB_URL = "postgresql://postgres:majid1214@localhost:5432/postgres"
# pool: AsyncConnectionPool[AsyncConnection[dict[str, Any]]] | None = None

# @asynccontextmanager
# async def lifespan(_app: FastAPI):
#     global pool 
#     _ = _app
#     async def configure(conn: AsyncConnection[dict[str, Any]]) -> None:
#         await register_vector_async(conn)

#     async with AsyncConnectionPool[AsyncConnection[dict[str, Any]]](
#         DB_URL, min_size =1, max_size=10,
#         kwargs = {'row_factory':dict_row},
#         configure = configure
#     ) as db_pool:
        
#         pool = db_pool

#         yield

# app = FastAPI(lifespan=lifespan)

# class HybridSearchQuery(BaseModel):
#     query_embedding: list[float]
#     text_query: str 
#     match_count: int = Field(default=5, le=10)

# @app.post('/documents/hybrid_search' , tags=['Rag Documents Search'])
# async def hybrid_vector_documents(search: HybridSearchQuery):
#     global pool 
#     if not pool:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail = 'database not initialized')
    
#     try:
#         async with pool.connection() as conn:
#             async with conn.cursor() as cur:
#                 await cur.execute(
#                     """
#                     WITH dense_search as (
#                             select id, user_name, content,search_vector, row_number() over (order by embedding <=> %s::vector) as rank
#                             from rag_documents
#                             order by embedding <=> %s::vector
#                             limit 5
#                         ),
#                     sparse_search as (
#                             select id, user_name, content,search_vector, row_number() over (order by ts_rank_cd(search_vector , plainto_tsquery('english', %s))DESC ) as rank
#                             from rag_documents
#                             order by search_vector @@ plainto_tsquery('english', %s)
#                             limit 5
#                     )
#                     select
#                         COALESCE(ds.id, ss.id ) AS id,
#                         COALESCE(ds.user_name, ss.user_name) AS user_name, 
#                         COALESCE(ds.content, ss.content ) AS content,
#                         COALESCE(ds.search_vector, ss.search_vector) as search_vector,
#                         (COALESCE(1.0/(60 + ds.rank) , 0.0) + COALESCE(1.0/(60 + ss.rank), 0.0)) as rrf_score
#                     from dense_search ds
#                     FULL OUTER JOIN sparse_search ss ON ds.id = ss.id
#                     order by rrf_score DESC
#                     limit %s;
#                     """, (search.query_embedding,
#                         search.query_embedding,
#                         search.text_query, 
#                         search.text_query ,
#                         search.match_count
#                         )
#                 )
#                 rows = await cur.fetchall()
#                 if not rows:
#                     return {'message': 'No matching documents found', 'results':[]}
#                 results = []
#                 for row in rows:
#                     results.append({
#                         'id' : str(row['id']),
#                         'user_name': row['user_name'],
#                         'content': row['content'],
#                         'search_vectory' : row['search_vector'],
#                         'rrf_score' : round(row['rrf_score'], 3)
#                     })

#                 return {
#                     'text_query' : search.text_query,
#                     'total_matches' : len(results),
#                     'results' : results
                    
#                 }
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# _______________________7________________________________________________
# Practice q7. Bulk Data Ingestion with Copy() protocol of asyncConnection


from contextlib import asynccontextmanager
from fastapi import FastAPI , HTTPException, status
from typing import Any
from pydantic import BaseModel, Field
from pgvector.psycopg import register_vector_async
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
import hashlib


DB_URL = "postgresql://postgres:majid1214@localhost:5432/postgres"
pool: AsyncConnectionPool[AsyncConnection[dict[str, Any]]] | None = None

@asynccontextmanager
async def lifespan(_app: FastAPI):
    global pool 
    _ = _app
    async def configure(conn: AsyncConnection[dict[str, Any]]) -> None:
        await register_vector_async(conn)

    async with AsyncConnectionPool[AsyncConnection[dict[str, Any]]](
        DB_URL, min_size =1, max_size=10,
        kwargs = {'row_factory':dict_row},
        configure = configure
    ) as db_pool:
        
        pool = db_pool

        yield

app = FastAPI(lifespan=lifespan)

class DocumentItem(BaseModel):
    user_name: str 
    content: str 
    embedding: list[float]

class BulkDocumentsIngestion(BaseModel):
    documents: list[DocumentItem]

@app.post('/documents/bulk-copy', tags=['Rag Bulk Ingestion'])
async def bulk_ingest_docs(payload: BulkDocumentsIngestion):
    global pool 
    if not pool:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail = 'database not initialized')
    
    try:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                async with cur.copy(
                    """
                    COPY rag_documents (user_name, content, embedding, content_hashing) FROM STDIN 
                    """
                ) as copy:
                    seen_hashes = set()
                    for doc in payload.documents:
                        content_hashing = hashlib.sha256(f"{doc.user_name}:{doc.content}:{doc.embedding}".encode('utf-8')).hexdigest()
                        if content_hashing in seen_hashes:
                            continue
                        seen_hashes.add(content_hashing)
                        formated_embedding = "["+",".join(map(str, doc.embedding))+"]"
                        await copy.write_row((doc.user_name, doc.content, formated_embedding, content_hashing))

                    return {
                        'status' : 'success',
                        'message' : f'Successfully Streamed {len(payload.documents)} via COPY protocol.'
                    }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
            




