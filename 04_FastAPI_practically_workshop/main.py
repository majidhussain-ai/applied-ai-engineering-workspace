from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from streaming_response import router_stream

app = FastAPI(
    title="Server-Sent Events (SSE) AI Streaming Infrastructure",
    description="Building ultra-low Time-To-First-Token (TTFT) text generators matching standard web streaming capabilities.",
    version="1.0.0"
)

# Real-world apps use tools like Next.js or React to hit this backend. CORS must allow stream headers!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down to your specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REGISTER THE LLM STREAMER ROUTER MODULE CLEANLY
app.include_router(router_stream)
