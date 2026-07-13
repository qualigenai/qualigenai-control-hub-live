from app.config import Settings

print("AUTH TYPE:", Settings.RAG_API_AUTH_TYPE)
print("TOKEN PRESENT:", bool(Settings.RAG_API_KEY))
print("HEADERS:", Settings.get_auth_headers().keys())