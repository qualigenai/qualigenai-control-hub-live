from app.connectors.auth_connector import AuthConnector

auth = AuthConnector()
result = auth.login()

print(result.get("status"))

if result.get("status") == "success":
    print("Auto-login successful")
    print("Token present:", bool(result.get("access_token")))
else:
    print("Auto-login failed")
    print(result.get("error"))