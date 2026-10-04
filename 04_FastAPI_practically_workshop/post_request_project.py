#1. Input Validation Schema: Post request first define incoming payload structure 
from typing import Annotated
from pydantic import BaseModel, Field, HttpUrl, EmailStr

# Custom Reusable Types using Annotated
SearchQuery = Annotated[str, Field(min_length=3, max_length=50, description="Main topic or keyword to search")]
MaxResults = Annotated[int, Field(default=5, ge=1, le=20, description="Number of items to return (1-20)")]
SourceUrls = Annotated[list[HttpUrl], Field(min_length=1, max_length=5, description="1 to 5 valid source URLs")]

# 1. Main Input Request Schema
class MultiSourceFetchRequest(BaseModel):
    query: SearchQuery
    max_results: MaxResults = 5
    sources: SourceUrls
    requested_by: EmailStr  # Pydantic validates valid email format automatically!


#2. Output Validation schema: This tells client exact how output format would be
from pydantic import BaseModel
from datetime import datetime

# Sub-model for individual processed source
class ProcessedSource(BaseModel):
    url: str
    status: str
    extracted_items_count: int

# 2. Main Response Schema
class MultiSourceFetchResponse(BaseModel):
    request_id: str
    query: str
    total_sources_processed: int
    created_at: datetime
    sources_summary: list[ProcessedSource]


#3. Complete Post Route Handler
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import FastAPI, status, HTTPException, Depends
import httpx

# ----------------------------------------------------
# 1. Lifespan Context Manager (Shared HTTP Engine)
# ----------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # App startup logic
    app.state.http_client = httpx.AsyncClient(timeout=10.0)
    print("🚀 Shared HTTP Engine connected")
    yield
    # App shutdown logic
    await app.state.http_client.aclose()
    print("🛑 Shared HTTP Engine closed")

app = FastAPI(title="Multi-Source Data Aggregator", lifespan=lifespan)

@app.get('/home', tags=['Home'])
async def home():
    return {
        'status' : 'Ok',
        'message' : 'Welcome to our website please explore more with endpoint'
    }
# Dependency to access shared HTTP client
def get_http_client(request) -> httpx.AsyncClient:
    return request.state.http_client

HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]

# ----------------------------------------------------
# 2. Complete POST Route Endpoint
# ----------------------------------------------------
@app.post(
    "/api/v1/aggregate-sources",
    response_model=MultiSourceFetchResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Multi-Source Processing"],
    summary="Fetch and aggregate data from multiple URLs"
)
async def process_multi_source_data(
    payload: MultiSourceFetchRequest,
    client: HttpClientDep
) -> MultiSourceFetchResponse:
    
    # Simple business logic handling
    processed_list: list[ProcessedSource] = []
    
    for source_url in payload.sources:
        # Converting HttpUrl object to standard string
        url_str = str(source_url)
        
        # Simulating data extraction process
        processed_list.append(
            ProcessedSource(
                url=url_str,
                status="processed",
                extracted_items_count=payload.max_results
            )
        )
    
    # Constructing response matching our Pydantic Output Model
    return MultiSourceFetchResponse(
        request_id=f"req_{uuid4().hex[:8]}",
        query=payload.query,
        total_sources_processed=len(processed_list),
        created_at=datetime.now(timezone.utc),
        sources_summary=processed_list
    )

