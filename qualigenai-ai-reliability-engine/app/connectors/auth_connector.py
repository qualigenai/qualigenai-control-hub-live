import requests

from app.config import Settings


class AuthConnector:
    """
    Handles authentication with the RAG v1.5 API.
    """

    def __init__(self):
        self.base_url = Settings.get_base_url().rstrip("/")
        self.login_endpoint = Settings.RAG_LOGIN_ENDPOINT
        self.timeout = Settings.REQUEST_TIMEOUT_SECONDS

    def login(self) -> dict:
        """
        Logs into the RAG API and returns a bearer token.
        """

        url = f"{self.base_url}{self.login_endpoint}"

        if not Settings.RAG_LOGIN_EMAIL or not Settings.RAG_LOGIN_PASSWORD:
            return {
                "status": "failed",
                "error": "Missing RAG_LOGIN_EMAIL or RAG_LOGIN_PASSWORD in .env"
            }

        payload_options = [
            {
                "email": Settings.RAG_LOGIN_EMAIL,
                "password": Settings.RAG_LOGIN_PASSWORD
            }
        ]

        last_error = None

        for payload in payload_options:
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )

                if response.status_code >= 400:
                    last_error = f"{response.status_code} Error: {response.text}"
                    continue

                data = response.json()

                access_token = data.get("access_token")
                token_type = data.get("token_type", "bearer")

                if not access_token:
                    return {
                        "status": "failed",
                        "error": "Login response did not contain access_token",
                        "response": data
                    }

                return {
                    "status": "success",
                    "access_token": access_token,
                    "token_type": token_type
                }

            except requests.exceptions.RequestException as error:
                last_error = str(error)

            except ValueError:
                last_error = "Login endpoint did not return valid JSON"

        return {
            "status": "failed",
            "error": last_error or "Unknown login error"
        }