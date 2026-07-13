import requests

from app.config import Settings
from app.connectors.auth_connector import AuthConnector
from app.utils.response_parser import RAGResponseParser


class RAGV15Connector:
    """
    Connector for Hybrid RAG v1.5.
    Supports manual bearer token and auto-login mode.
    """

    def __init__(self):
        self.base_url = Settings.get_base_url().rstrip("/")
        self.query_endpoint = Settings.RAG_QUERY_ENDPOINT
        self.health_endpoint = Settings.RAG_HEALTH_ENDPOINT
        self.timeout = Settings.REQUEST_TIMEOUT_SECONDS
        self.parser = RAGResponseParser()
        self.auth_headers = self._build_auth_headers()

    def _build_auth_headers(self) -> dict:
        """
        Builds auth headers either from .env bearer token or auto-login.
        """

        if Settings.RAG_API_AUTH_TYPE == "auto_login":
            auth_connector = AuthConnector()
            login_result = auth_connector.login()

            if login_result.get("status") == "success":
                access_token = login_result.get("access_token")
                return {
                    "Authorization": f"Bearer {access_token}"
                }

            print("WARNING: Auto-login failed.")
            print(login_result.get("error"))
            return {}

        return Settings.get_auth_headers()

    def health_check(self) -> dict:
        url = f"{self.base_url}{self.health_endpoint}"

        try:
            response = requests.get(
                url,
                headers=self.auth_headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            return {
                "status": "success",
                "url": url,
                "data": response.json()
            }

        except requests.exceptions.RequestException as error:
            return {
                "status": "failed",
                "url": url,
                "error": str(error)
            }

        except ValueError:
            return {
                "status": "failed",
                "url": url,
                "error": "Health endpoint did not return valid JSON"
            }

    def ask_question(self, test_id: str, question: str) -> dict:
        url = f"{self.base_url}{self.query_endpoint}"

        payload = {
            "query_text": question
        }

        try:
            response = requests.post(
                url,
                data=payload,
                headers=self.auth_headers,
                timeout=self.timeout
            )

            if response.status_code >= 400:
                return {
                    "status": "failed",
                    "test_id": test_id,
                    "url": url,
                    "question": question,
                    "error": f"{response.status_code} Error: {response.text}"
                }

            raw_data = response.json()
            parsed_data = self.parser.parse(raw_data)

            return {
                "status": "success",
                "test_id": test_id,
                "url": url,
                "payload_used": payload,
                "data": parsed_data
            }

        except requests.exceptions.RequestException as error:
            return {
                "status": "failed",
                "test_id": test_id,
                "url": url,
                "question": question,
                "error": str(error)
            }

        except ValueError:
            return {
                "status": "failed",
                "test_id": test_id,
                "url": url,
                "question": question,
                "error": "Query endpoint did not return valid JSON"
            }