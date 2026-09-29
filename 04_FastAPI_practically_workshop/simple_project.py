# open the json file from link
from fastapi import FastAPI, status, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated
import httpx

# path_url = "https://microsoftedge.github.io/Demos/json-dummy-data/64KB.json"
path_url = 'https://jsonlint.com/datasets/countries.json'

app = FastAPI(title="Country Finder and Sorter API")

@app.get('/main', tags=['Main'])
async def main():
    return {
        'message': 'Welcome to our Website'
    }

async def load_data():
    async with httpx.AsyncClient() as client: 
        response = await client.get(path_url)
        response.raise_for_status()
        return response.json()

@app.get('/view', tags=['ViewUsersDetail'])
async def view_user_data():
    data = await load_data()
    return {
        'status' : 'success',
        'data' : data[:3]
    }

# @app.get('/fetch_single_user/{name}', tags=['FetchSingleUserDetail'])
# async def user_detail(
#     name: Annotated[str, Path(description='Enter Name See Detail Specific User.', examples=["Majid Hussain"])]
# ):
#     data_list = await load_data()
    
#     for user in data_list:
#         if user.get("name") == name:
#             # Pura user object return karein jab match ho jaye
#             return {
#                 "status": "success",
#                 "data": user
#             }
            
#     # Agar loop end ho jaye aur matching id na mile
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND, 
#         detail='User not found with the provided Name'
#     )

# @app.get('/sorted', tags=['Sorting'])
# async def sorting_by_name(
#     sorted_by: Annotated[str, Query(description=("Sorted between Ascending or Descending"))] = 'desc'):
#     data = await load_data()
#     list_countries = data.get('countries', [])
#     if not list_countries:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "List is empty or URL changes")

#     if sorted_by not in ['asc', 'desc']:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Choose between asc or desc')

#     sort_by = True if sorted_by == 'desc' else False
#     sort_data = sorted(list_countries , key=lambda x: x.get('name', 0), reverse=sort_by)
#     return sort_data

# sorting by population 
@app.get('/population', tags=['Population'])
async def sort_by_populaction(
    sorted_by: Annotated[str, Query(description='Either ascending or descending')]):
    raw_data = await load_data()
    list_population = raw_data.get('countries', [])
    if not list_population:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cannot load successfully URL or Modify URL.')

    if sorted_by not in ['Highest', 'Lowest']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Eidhar Highest or Lowest')

    is_reverse = True if sorted_by == 'Highest' else False
    sorted_data = sorted(list_population, key=lambda x: x.get('population', 0), reverse=is_reverse)
    return sorted_data[:4]