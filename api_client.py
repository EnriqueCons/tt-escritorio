# api_client.py
import requests, json

API_BASE_URL = "http://localhost:8080"

class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self._access_token = None

    def set_access_token(self, token: str | None):
        self._access_token = token

    def clear_token(self):
        self._access_token = None

    def headers(self):
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._access_token:
            h["Authorization"] = f"Bearer {self._access_token}"
        return h

    # ---- Endpoints útiles ----
    def post_json(self, path, payload, timeout=10):
        url = f"{self.base_url}{path}"
        return self.session.post(url, data=json.dumps(payload),
                                 headers=self.headers(), timeout=timeout)

    def post_logout(self, path="/api/auth/admin/logout", timeout=6):
        url = f"{self.base_url}{path}"
        return self.session.post(url, headers=self.headers(), timeout=timeout)

api = ApiClient(API_BASE_URL)
