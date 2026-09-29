from fastapi import FastAPI, status, Path
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI(title='This is my first program')

# example1. 
# @app.get('/', tags=['General', 'Important'])
# async def home():
#     return {'status':'success', 'message' : 'This is my first program'}

# @app.get('/about_me', tags=['BioGraphy'])
# async def about():
#     return {'status': 'ok' , 'message': 'Hy! How can I help you'}

# # path parameters
# @app.get('/users/{item_id}', tags=['Users'])
# async def get_items(item_id: int):
#     return {
#         'item_id':item_id,
#         'description' : f'Details for item number {item_id}'
#     }

# @app.get('/search', tags=['Search'])
# def get_search(category: str, limits: int = 5):
#     return {
#         'category' : category,
#         'limits' : limits,
#         'description' : f'showing top {limits} items in {category}'
#     }


# input schema
class DocumentPayload(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=100, description='Title of the docs')]
    content: Annotated[str, Field(min_length=10, description='Content of the Docs')]
    priority: Annotated[int, Field(default=1, ge=1, le=5, description='Scale them from 1 to 5')]

# output schema 
class DocumentResponse(BaseModel):
    status: str
    document_id: int 
    title: str 
    token_count: int

@app.post('/documents' , response_model=DocumentResponse,status_code=status.HTTP_201_CREATED, tags=['Documents'])
async def create_documents(payload: DocumentPayload):
    count_tokens = payload.content.split()
    total_words = len(count_tokens)

    generated_id = 101
    return {
        'status' : 'Created Documents successfully',
        'document_id': generated_id,
        'title': payload.title,
        'token_count': total_words
    }

