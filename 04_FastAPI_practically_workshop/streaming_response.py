import asyncio
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Annotated

router_stream = APIRouter(prefix="/api/v1/llm", tags=["AI Streaming Operations"])

class ChatPromptPayload(BaseModel):
    user_prompt: Annotated[str, Field(..., min_length=2, description="The chat prompt message for the AI model.", examples=["Explain quantum computing simply"])]

async def dummy_llm_token_generator(prompt: str):
    """
    Simulating a local or external LLM (like OpenAI/Ollama) yielding text token-by-token.
    Standard SSE format requires data to be wrapped as 'data: <message>\n\n'.
    """
    sample_text = (
        f"Artificial Intelligence Response for prompt '{prompt}':\n"
        "Quantum computing is a rapidly-emerging technology that harnesses "
        "the laws of quantum mechanics to solve problems too complex for classical computers. "
        "Instead of bits (0s and 1s), it uses qubits which can exist in a state of superposition."
    )
    
    tokens_list = sample_text.split(" ")
    try:
        for token in tokens_list:
            sse_formatted_chunk = f"data: {token} \n\n"
            yield sse_formatted_chunk
            await asyncio.sleep(0.6)
    except asyncio.CancelledError:
        # Agar user chat window close kar deta hai ya browser reload karta hai,
        # to FastAPI is generator loop ko instantly terminate kar deta hai taake GPU compute resource waste na ho!
        print("[Streaming Connection Cancelled] User disconnected. Terminating LLM execution thread context.")
        return
    
@router_stream.post("/chat-stream", status_code=status.HTTP_200_OK)
async def stream_chat_inference(payload: ChatPromptPayload):
    """
    Ingest a prompt string and open a unidirectional, long-running HTTP text/event-stream connection 
    to yield generated LLM response fragments token-by-token directly back to the client interface.
    """
    print(f"Ingesting streaming request for prompt context: '{payload.user_prompt}'")
    
    # Step 1: Initialize the custom async generator handler
    token_generator_instance = dummy_llm_token_generator(payload.user_prompt)
    
    # Step 2: Return a StreamingResponse object wrapping our token generator
    # 'media_type' must be explicitly set to 'text/event-stream' for modern SSE setups
    return StreamingResponse(
        token_generator_instance,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache", # Tells the browser not to cache chunks
            "Connection": "keep-alive",  # Standard configuration keeping the wire open
            "X-Accel-Buffering": "no"    # Disables Nginx buffering so chunks pass through instantly in production
        }
    )
