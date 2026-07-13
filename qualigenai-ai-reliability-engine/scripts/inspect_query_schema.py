import requests
import json

url = "http://127.0.0.1:8000/openapi.json"

response = requests.get(url, timeout=30)
response.raise_for_status()

openapi = response.json()

paths = openapi.get("paths", {})

print("Available paths:")
for path in paths.keys():
    print(path)

print("\n/query schema:")
query_schema = paths.get("/query", {})
print(json.dumps(query_schema, indent=2))