from fastapi import FastAPI, status

app = FastAPI(title='This is my first program', status_code = status.HTTP_200_OK)

@app.get('/', tags=['General', 'Important'])
async def home():
    return {'status':'success', 'message' : 'This is my first program'}

@app.get('/about_me', tags=['BioGraphy'])
async def about():
    return {'status': 'ok' , 'message': 'Hy! How can I help you'}

# path parameters
@app.get('/users/{item_id}', tags=['Users'])
async def get_items(item_id: int):
    return {
        'item_id':item_id,
        'description' : f'Details for item number {item_id}'
    }

@app.get('/search', tags=['Search'])
def get_search(category: str, limits: int = 5):
    return {
        'category' : category,
        'limits' : limits,
        'description' : f'showing top {limits} items in {category}'
    }
