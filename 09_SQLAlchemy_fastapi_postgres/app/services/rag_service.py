import io
import asyncio
import logging
from typing import Any
from pypdf import PdfReader
from google import genai
from google.genai import errors, types

from app.config import settings

# Initialize Gemini Client once
logger = logging.getLogger('uvicorn.errors')
gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"
GENERATION_MODELS = [
    "gemini-3.5-flash-lite",  
    "gemini-3.5-flash",       
    "gemini-3.7-flash",      
    "gemini-3.8-flash",      
    "gemma-4-31b-it",        
]

def extract_text_from_file(file_bytes: bytes, filename: str) -> list[dict[str, Any]]:
    """
    Extracts text from .pdf or .txt files.
    Returns a list of dicts: [{"text": "...", "metadata": {"page": 1}}]
    """
    ext = filename.lower().split(".")[-1]
    extracted_pages: list[dict[str, Any]] = []

    if ext == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_pages.append(
                    {
                        "text": page_text.strip(),
                        "metadata": {"page_number": page_num, "source": filename},
                    }
                )
    elif ext == "txt":
        text_content = file_bytes.decode("utf-8", errors="ignore").strip()
        if text_content:
            extracted_pages.append(
                {
                    "text": text_content,
                    "metadata": {"page_number": 1, "source": filename},
                }
            )
    else:
        raise ValueError(f"Unsupported file format: .{ext}. Only .pdf and .txt are allowed.")

    return extracted_pages


def chunk_extracted_pages(
    pages: list[dict[str, Any]],
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[dict[str, Any]]:
    """
    Splits extracted page texts into overlapping semantic chunks while preserving metadata.
    """
    chunks: list[dict[str, Any]] = []
    chunk_index = 0

    for page in pages:
        text = page["text"]
        base_meta = page["metadata"]
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "content": chunk_text,
                        "chunk_metadata": {
                            **base_meta,
                            "char_length": len(chunk_text),
                        },
                    }
                )
                chunk_index += 1

            # Move window forward with overlap
            start += chunk_size - chunk_overlap

    return chunks


async def generate_document_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Asynchronously generates 1536-dim embeddings for a batch of document chunks.
    """
    response = await gemini_client.aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=1536,
        ),
    )

    embeddings = response.embeddings or []
    if not embeddings:
        raise ValueError("No embedding values were returned for the document batch.")

    normalized_embeddings: list[list[float]] = []
    for embedding in embeddings:
        values = embedding.values
        if values is None:
            raise ValueError("One or more document embeddings are missing values.")
        normalized_embeddings.append(list(values))

    return normalized_embeddings


async def generate_query_embedding(query: str) -> list[float]:
    """
    Asynchronously generates a 1536-dim embedding for a single user search query.
    """
    response = await gemini_client.aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=1536,
        ),
    )

    embeddings = response.embeddings or []
    if not embeddings or embeddings[0].values is None:
        raise ValueError("No embedding values were returned for the query.")

    return list(embeddings[0].values)
async def generate_rag_answer(query: str, context_chunks: list[str]) -> str:
    """
    Fast RAG generation with strict 8-second timeout per model and instant fallback.
    """
    formatted_context = "\n\n---\n\n".join(context_chunks)
    prompt = (
        "You are a precise AI assistant. Answer the user's question ONLY using the provided context.\n"
        "If the answer is not present in the context, clearly state that the provided documents do not contain this information.\n\n"
        f"CONTEXT:{formatted_context}"
        f"USER QUESTION:\n{query}"
    )

    last_error: Exception | None = None

    for model_name in GENERATION_MODELS:
        try:
            logger.info(f"⚡ Trying fast generation with: {model_name}")
            # Strict 10-second timeout prevents SDK internal tenacity retries from hanging for minutes!
            response = await asyncio.wait_for(
                gemini_client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                ),
                timeout=10.0,
            )
            if response.text:
                logger.info(f"✅ Answered in seconds using: {model_name}")
                return response.text

        except TimeoutError as err:
            logger.warning(
                f"⏱️ '{model_name}' took >10s (stuck in server queue). Instantly switching to next model..."
            )
            last_error = err
            continue

        except errors.APIError as err:
            logger.warning(
                f"⚠️ '{model_name}' failed ({err.code} {err.status}). Instantly switching to next model..."
            )
            last_error = err
            continue

    raise RuntimeError(
        f"All fallback Gemini models failed. Last error: {last_error}"
    )