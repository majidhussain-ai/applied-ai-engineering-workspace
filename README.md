# Async Hybrid RAG Engine — FastAPI, PostgreSQL (`pgvector`), & Gemini

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-336791?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%20Async-red)
![Gemini](https://img.shields.io/badge/Google%20GenAI-Gemini%20Models-4285F4?logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

A production-grade, fully asynchronous **Retrieval-Augmented Generation (RAG)** backend engineered with **FastAPI**, **SQLAlchemy 2.0 (`psycopg` v3 async)**, **PostgreSQL (`pgvector`)**, and the **Google GenAI SDK**.

Unlike basic RAG prototypes that rely on in-memory vector stores or pure top-$k$ retrieval, this system implements **Hybrid Search**—combining **HNSW Cosine Vector Similarity**, **Relational Pre-filtering**, **PostgreSQL JSONB GIN Metadata Indexing**, and **Strict Cosine Distance Thresholding**, paired with **Automated Multi-Model Fallback & Latency Guardrails**.

---

## System Architecture & Key Engineering Highlights

1. **100% Non-Blocking Async I/O Pipeline:**
   - End-to-end `async`/`await` architecture from FastAPI route handlers down to PostgreSQL (`psycopg` v3 async driver) and Google GenAI's async client (`client.aio`).
   - CPU-bound PDF parsing (`pypdf`) offloaded via `asyncio.to_thread` to prevent event-loop blocking.

2. **Hybrid Vector + Relational + JSONB Retrieval:**
   - **HNSW Vector Index (`vector_cosine_ops`):** Sub-millisecond Approximate Nearest Neighbor (ANN) search over `1536`-dimensional `gemini-embedding-001` vectors (`m=16`, `ef_construction=64`).
   - **GIN Metadata Index (`JSONB`):** High-speed metadata containment filtering (`@>` operator) for page-level (`{"page_number": 1}`) or source-level (`{"source": "report.pdf"}`) scoping prior to vector scoring.
   - **Similarity Threshold Guardrails (`max_distance`):** Filters out noisy/irrelevant chunks at the SQL level (`WHERE (embedding <=> query_vec) <= max_distance`) before invoking the LLM, saving token costs and preventing hallucinations.

3. **Resilient Multi-Model LLM Orchestration:**
   - Automatic model fallback cascade (`gemini-3.5-flash-lite` $\rightarrow$ `gemini-3.5-flash` $\rightarrow$ `gemini-3.7-flash` $\rightarrow$ `gemini-3.8-flash` $\rightarrow$ `gemma-4-31b-it`).
   - Enforces a strict per-attempt `asyncio.wait_for` timeout (`10.0s`) to bypass upstream `503 UNAVAILABLE` traffic spikes or `429` rate limits with zero downtime.

4. **Atomic Transactions & N+1 Prevention:**
   - Uses `session.flush()` to generate parent primary keys in-memory before bulk-inserting child document chunks within a single atomic commit.
   - Eliminates `MissingGreenlet` lazy-loading errors in async contexts via explicit `selectinload()` eager loading.

---

## Project Structure

```text
├── alembic/                        # Async Alembic migration environment & revision history
│   ├── versions/                   # Schema migrations (Users, Documents, Chunks, HNSW & GIN indexes)
│   └── env.py                      # AsyncEngine migration runner
├── app/
│   ├── api/v1/
│   │   ├── users.py                # User registration & profile retrieval endpoints
│   │   └── documents.py            # Ingestion (/upload), Hybrid Search (/search), & RAG QA (/ask)
│   ├── crud/
│   │   ├── user.py                 # Async User CRUD operations
│   │   └── document.py             # Atomic document/chunk insertion & Hybrid pgvector queries
│   ├── models/
│   │   ├── base.py                 # SQLAlchemy 2.0 DeclarativeBase, UUIDPKMixin, TimestampMixin
│   │   ├── user.py                 # User ORM model
│   │   └── document.py             # Document & DocumentChunk ORM models (Vector(1536), JSONB, HNSW, GIN)
│   ├── schemas/
│   │   ├── user.py                 # Pydantic V2 User schemas
│   │   └── document.py             # Pydantic V2 Document, Chunk, & ScoredChunkRead schemas
│   ├── services/
│   │   └── rag_service.py          # PDF/TXT extraction, sliding-window chunker, Gemini embeddings & LLM fallback
│   ├── config.py                   # Pydantic BaseSettings (.env configuration)
│   ├── database.py                 # AsyncEngine & AsyncSession dependency injection
│   └── main.py                     # FastAPI application entrypoint
├── tests/
│   └── test_rag_api.py             # End-to-end async integration tests (pytest-asyncio + httpx ASGITransport)
├── Dockerfile                      # Production Python 3.12 container image
├── docker-compose.yml              # Multi-container orchestration (FastAPI + pgvector/pgvector:pg16)
├── alembic.ini                     # Alembic configuration
├── pytest.ini                      # Pytest async loop configuration
└── requirements.txt                # Project dependencies
```

---

## Getting Started

### Option 1: Run with Docker Compose (Recommended)

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/async-hybrid-rag-pgvector.git
   cd async-hybrid-rag-pgvector
   ```

2. **Configure environment variables:**
   Create a `.env` file in the root directory:

   ```env
   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag_db
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

3. **Build and start the containers:**
   ```bash
   docker compose up --build
   ```
   _Docker Compose automatically launches `pgvector/pgvector:pg16`, waits for the healthcheck, runs `alembic upgrade head`, and starts the FastAPI server at `http://localhost:8000`._

---

### Option 2: Local Setup (Ubuntu / Linux)

1. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Ensure PostgreSQL & `pgvector` are running locally, then apply migrations:**

   ```bash
   alembic upgrade head
   ```

3. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Open Interactive Swagger UI at: **`http://127.0.0.1:8000/docs`**

---

## Core API Endpoints

| Method | Endpoint                   | Description                                                                                                        |
| :----- | :------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| `POST` | `/api/v1/users/`           | Register a new user and obtain a `user_id` (`UUID`)                                                                |
| `POST` | `/api/v1/documents/upload` | Upload `.pdf` or `.txt` files $\rightarrow$ auto-chunk $\rightarrow$ batch embed $\rightarrow$ store in `pgvector` |
| `POST` | `/api/v1/documents/search` | Direct hybrid semantic search returning `distance` and `similarity_score`                                          |
| `POST` | `/api/v1/documents/ask`    | End-to-end RAG QA with optional `document_id`, `metadata_filter`, and `max_distance`                               |

### Example `/api/v1/documents/ask` Request Payload:

```json
{
  "question": "What are the core deliverables in Month 1?",
  "top_k": 4,
  "max_distance": 0.55,
  "document_id": null,
  "metadata_filter": {
    "page_number": 1
  }
}
```

---

## 🧪 Running Automated Tests

The test suite uses `pytest-asyncio` and `httpx.AsyncClient` (`ASGITransport`) with deterministic LLM/Embedding mocking to validate the full database and vector retrieval pipeline in ~1 second without consuming API quota:

```bash
pytest -v
```

---

## Author

**Majid Hussain**  
_Applied AI & Backend Engineer_
