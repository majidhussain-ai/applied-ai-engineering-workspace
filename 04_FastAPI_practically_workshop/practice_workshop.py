from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/user-info")
async def get_user_info(request: Request):
    # Direct Request object se metadata read karna
    client_ip = request.client.host if request.client else "Unknown"
    user_agent = request.headers.get("user-agent", "Unknown")
    
    return {
        "client_ip": client_ip,
        "user_agent": user_agent,
        "method": request.method,
        "url": str(request.url)
    }