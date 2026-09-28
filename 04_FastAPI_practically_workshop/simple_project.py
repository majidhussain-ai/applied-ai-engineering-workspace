# open the json file from link
from fastapi import FastAPI
import json
import asyncio 
import httpx

path_url = "https://microsoftedge.github.io/Demos/json-dummy-data/64KB.json"

async def load_data():
    async with httpx.AsyncClient() as client: 
        response = await client.get(path_url)
        response.raise_for_status()
        json_data = response.json()
        return (json_data, f"status code: {response.status_code}")

app = FastAPI()
@app.get('/view')
async def view_user_data():
    data = await load_data()
    return data
