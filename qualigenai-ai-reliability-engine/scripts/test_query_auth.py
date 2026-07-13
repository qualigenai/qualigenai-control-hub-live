import requests
from app.config import Settings

url = "http://127.0.0.1:8000/query"

payload = {
    "query_text": "What is Hybrid RAG?"
}

print("Headers being sent:", Settings.get_auth_headers().keys())
print("Payload being sent:", payload)

response = requests.post(
    url,
    data=payload,
    headers=Settings.get_auth_headers(),
    timeout=60
)

print("Status:", response.status_code)
print("Response:")
print(response.text[:2000])