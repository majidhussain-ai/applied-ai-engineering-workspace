import io
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client():
    """In-memory async HTTP client connected directly to the FastAPI ASGI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


async def test_health_check(async_client: AsyncClient):
    """1. Verify root/docs availability."""
    response = await async_client.get("/docs")
    assert response.status_code == 200


async def test_full_rag_lifecycle(async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """
    2. End-to-End Test:
    Create User -> Upload .txt File -> Store in pgvector -> Ask Question with Threshold & Filter.
    """
    # --- A. Mock Gemini API functions to make tests instant & free ---
    fake_vector = [0.02] * 1536  # Valid 1536-dim vector for pgvector

    async def mock_doc_embeddings(texts: list[str]) -> list[list[float]]:
        return [fake_vector for _ in texts]

    async def mock_query_embedding(query: str) -> list[float]:
        return fake_vector

    async def mock_rag_answer(query: str, context_chunks: list[str]) -> str:
        return f"Mocked AI Answer based on {len(context_chunks)} retrieved chunk(s)."

    monkeypatch.setattr(
        "app.api.v1.documents.generate_document_embeddings", mock_doc_embeddings
    )
    monkeypatch.setattr(
        "app.api.v1.documents.generate_query_embedding", mock_query_embedding
    )
    monkeypatch.setattr(
        "app.api.v1.documents.generate_rag_answer", mock_rag_answer
    )

    # --- B. Create a Unique Test User ---
    unique_suffix = uuid.uuid4().hex[:6]
    user_payload = {
        "username": f"testuser_{unique_suffix}",
        "email": f"test_{unique_suffix}@example.com",
        "password": "securepassword123",
    }
    user_res = await async_client.post("/api/v1/users/", json=user_payload)
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    # --- C. Upload an In-Memory .txt File to /api/v1/documents/upload ---
    sample_text = (
        "FastAPI and SQLAlchemy 2.0 with pgvector enable high-speed HNSW vector similarity search. "
        "Hybrid retrieval combines relational filters and JSONB GIN indexes."
    )
    file_bytes = io.BytesIO(sample_text.encode("utf-8"))

    upload_res = await async_client.post(
        "/api/v1/documents/upload",
        data={"user_id": user_id},
        files={"file": ("test_guide.txt", file_bytes, "text/plain")},
    )
    assert upload_res.status_code == 201
    doc_data = upload_res.json()
    doc_id = doc_data["id"]
    assert doc_data["title"] == "test_guide.txt"
    assert len(doc_data["chunks"]) >= 1

    # --- D. Test /api/v1/documents/ask with Document Filter & Similarity Score ---
    ask_payload = {
        "question": "How does hybrid retrieval work?",
        "top_k": 3,
        "max_distance": 0.55,
        "document_id": doc_id,
        "metadata_filter": {"page_number": 1},
    }
    ask_res = await async_client.post("/api/v1/documents/ask", json=ask_payload)
    assert ask_res.status_code == 200

    rag_data = ask_res.json()
    assert "Mocked AI Answer" in rag_data["answer"]
    assert len(rag_data["sources"]) >= 1
    # Verify exact cosine distance (0.0) & similarity score (1.0) since query == chunk vector
    assert rag_data["sources"][0]["distance"] == 0.0
    assert rag_data["sources"][0]["similarity_score"] == 1.0