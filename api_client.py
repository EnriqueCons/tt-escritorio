import json
import requests

API_BASE_URL = "http://localhost:8080"

class ApiClient:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self._access_token = None

    def _url(self, path: str) -> str:
        base = getattr(self, "base_url", "http://localhost:8080").rstrip("/")
        return f"{base}/{path.lstrip('/')}"

    def set_access_token(self, token: str | None):
        self._access_token = token

    def headers(self):
        h = {"Accept": "application/json"}
        if self._access_token:
            h["Authorization"] = f"Bearer {self._access_token}"
        return h

    def get_json(self, path, params=None, headers=None, timeout=None):
        h = {"Accept": "application/json"}
        if headers:
            h.update(headers)
        return requests.get(
            self._url(path),
            params=params,
            headers=h,
            timeout=timeout or getattr(self, "timeout", 15),
        )

    def put_json(self, path, payload: dict, headers=None, timeout=None):
        h = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if headers:
            h.update(headers)
        return requests.put(
            self._url(path),
            data=json.dumps(payload),
            headers=h,
            timeout=timeout or getattr(self, "timeout", 15),
        )

    def post_json(self, path, payload, timeout=10):
        url = f"{self.base_url}{path}"
        h = self.headers().copy()
        return self.session.post(url, json=payload, headers=h, timeout=timeout)

    def clear_token(self):
        self._access_token = None

    def post_logout(self, path="/api/auth/admin/logout", timeout=6):
        url = f"{self.base_url}{path}"
        return self.session.post(url, headers=self.headers(), timeout=timeout)
    
    def delete(self, path, headers=None, timeout=None):
        h = {"Accept": "application/json"}
        if headers:
            h.update(headers)
        return requests.delete(
            self._url(path),
            headers=h,
            timeout=timeout or getattr(self, "timeout", 15)
        )
    
    def create_combate(self, payload: dict, timeout=15) -> dict:
        """
        POST /apiCombates/combate
        Devuelve el JSON del combate creado (incluyendo su id).
        """
        r = self.post_json("/apiCombates/combate", payload, timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else {}

    def prepare_combate(self, combate_id: int, timeout=10) -> str:
        """
        POST /apiCombates/combate/{id}/prepare
        Prepara el registro de sockets (rojo/azul) para ese combate.
        """
        url = f"{self.base_url}/apiCombates/combate/{combate_id}/prepare"
        r = self.session.post(url, headers=self.headers(), timeout=timeout)
        if r.status_code == 404:
            raise RuntimeError(f"Combate {combate_id} no encontrado en el servidor.")
        r.raise_for_status()
        return r.text or "OK"

api = ApiClient()
