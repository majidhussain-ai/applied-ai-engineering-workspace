from google import genai
from app.config import settings

gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Tamam models aur unke supported methods print karein
for m in gemini_client.models.list():
    print(f"Model Name: {m.name}")
    print(f"Supported Actions: {m.supported_actions}\n")