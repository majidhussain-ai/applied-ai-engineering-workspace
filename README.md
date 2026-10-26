# 🚀 Applied AI Engineering Workspace — 7-Month Production Stack

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Async%20APIs-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector%20HNSW-336791?logo=postgresql&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?logo=pytorch&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-1C3C3C)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)

A structured, code-first **Applied AI Engineering** monorepo documenting a 7-month progression from core asynchronous backend systems to deep learning internals, hybrid vector search architectures, multi-agent orchestration, and containerized production deployment.

---

## 🗺️ 7-Month Engineering Architecture & Stack

### Phase 1: Core Python, Async Concurrency & Data Validation (Month 1)
* **Core Stack:** Python 3.12+, `asyncio`, `httpx`, Pydantic V2, `pathlib`, Custom Logging & Exceptions.
* **Key Implementations:**
  * Object-Oriented Programming (OOP), magic methods, custom decorators, iterators, and memory-efficient generators.
  * High-concurrency non-blocking I/O pipelines using `asyncio.TaskGroup`, `asyncio.Semaphore`, `asyncio.timeout`, and `asyncio.to_thread` with `httpx.AsyncClient`.
  * Strict data parsing and payload validation using Pydantic V2 (`BaseModel`, `@field_validator`, `@model_validator`, `TypeAdapter`, and `Annotated`).

### Phase 2: Backend API Engineering & Relational Databases (Month 1–2)
* **Core Stack:** FastAPI, SQLAlchemy 2.0 (Async), PostgreSQL, `psycopg` v3, Alembic.
* **Key Implementations:**
  * Modular RESTful APIs (`GET`, `POST`, `PATCH`, `DELETE`) with Dependency Injection (`Depends`) and strict Pydantic response contracts.
  * Asynchronous database architecture with `UUID` primary keys, atomic transactions (`flush` / `commit`), batch `ON CONFLICT` upserts, keyset/offset pagination, and eager loading (`selectinload`) to prevent `MissingGreenlet` N+1 errors.
  * Database schema versioning and automated migrations with Async Alembic.

### Phase 3: Deep Learning Internals & Transformer Mechanics (Month 2–3)
* **Core Stack:** PyTorch, Hugging Face `transformers`, `tokenizers`, NumPy.
* **Key Implementations:**
  * Custom `nn.Module` neural network architectures and tensor manipulation.
  * **PyTorch Forward & Backward Hooks** (`register_forward_hook`) for inspecting internal layer activations, gradients, and representation geometry.
  * Self-attention mechanics, tokenization pipelines, and high-dimensional embedding space analysis.

### Phase 4: Production Hybrid RAG & Vector Search (Month 3–4)
* **Core Stack:** PostgreSQL (`pgvector`), Google GenAI SDK (`gemini-embedding-001` & Gemini Flash/Pro), `pypdf`, Redis.
* **Key Implementations:**
  * Real-time `.pdf` and `.txt` multipart ingestion with sliding-window chunking and batch vector embedding generation (`1536` dimensions).
  * **Hybrid Retrieval Engine:** Combines **HNSW Cosine Distance (`<=>`)**, relational foreign-key scoping (`document_id`), and **JSONB GIN Index (`@>`)** metadata filtering.
  * **Similarity Threshold Guardrails (`max_distance`):** SQL-level filtering to drop low-relevance noise chunks and return normalized `similarity_score` metrics.
  * **Resilient LLM Orchestration:** Automated multi-model fallback cascade with strict `asyncio.wait_for` latency protection against `503`/`429` API spikes.

### Phase 5: Agentic AI Workflows & Multi-Agent Systems (Month 5)
* **Core Stack:** LangGraph, LangChain Core, Structured Tool Calling, `AsyncPostgresSaver`.
* **Key Implementations:**
  * Stateful, cyclic agent graphs (`StateGraph`) with conditional routing and ReAct reasoning loops.
  * Persistent memory checkpointing and Human-in-the-Loop (HITL) execution interrupts.
  * Autonomous multi-agent workflows (e.g., Automated Research & Blog Generation System, AI Trip Planner).

### Phase 6: Model Context Protocol (MCP) & Fine-Tuning (Month 6)
* **Core Stack:** Anthropic MCP SDK, Hugging Face `PEFT` (LoRA / QLoRA), `TRL`, `bitsandbytes`.
* **Key Implementations:**
  * Building custom **MCP Servers and Clients** to standardize how LLMs securely query local file systems, PostgreSQL databases, and external APIs.
  * Parameter-Efficient Fine-Tuning (LoRA/QLoRA) of open-weights models on domain-specific instruction datasets.

### Phase 7: Testing, Containerization & Cloud MLOps (Month 7)
* **Core Stack:** `pytest-asyncio`, `httpx` (`ASGITransport`), Docker, Docker Compose, GitHub Actions.
* **Key Implementations:**
  * Fast, deterministic async integration testing with mocked LLM/embedding layers.
  * Multi-container orchestration (`Dockerfile` + `pgvector/pgvector:pg16`) with automated healthchecks (`pg_isready`) and zero-downtime migration startups.

---

## 🛠️ Tech Stack Summary

| Category | Technologies |
| :--- | :--- |
| **Languages & Runtime** | Python 3.12+, SQL, Bash, Linux (Ubuntu LTS) |
| **Backend & APIs** | FastAPI, Pydantic V2, Uvicorn, `httpx`, `asyncio` |
| **Databases & Vector Search** | PostgreSQL 16, `pgvector` (HNSW), SQLAlchemy 2.0 (Async), Alembic, JSONB (GIN) |
| **AI, LLMs & Agents** | Google GenAI SDK (Gemini), LangGraph, Model Context Protocol (MCP), PyTorch, Hugging Face |
| **DevOps & Testing** | Docker, Docker Compose, `pytest`, `pytest-asyncio`, Git |

---

## 👨‍💻 Author

**Majid Hussain**  
*Software & Applied AI Engineer*
*contact: majidhussain.ai5@gmail.com*
