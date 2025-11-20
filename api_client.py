import json
import requests
from config import API_BASE_URL, DEFAULT_TIMEOUT

class ApiClient:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self._access_token = None
        self.timeout = DEFAULT_TIMEOUT

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

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
            timeout=timeout or self.timeout,
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
            timeout=timeout or self.timeout,
        )

    def post_json(self, path, payload, timeout=None):
        url = f"{self.base_url}{path}"
        h = self.headers().copy()
        h["Content-Type"] = "application/json"
        return self.session.post(
            url, 
            json=payload, 
            headers=h, 
            timeout=timeout or self.timeout
        )

    def delete(self, path, headers=None, timeout=None):
        h = {"Accept": "application/json"}
        if headers:
            h.update(headers)
        return requests.delete(
            self._url(path),
            headers=h,
            timeout=timeout or self.timeout
        )

    def clear_token(self):
        self._access_token = None

    def post_logout(self, path="/api/auth/admin/logout", timeout=6):
        url = f"{self.base_url}{path}"
        return self.session.post(url, headers=self.headers(), timeout=timeout)
    
    # ============ ENDPOINTS DE COMBATES ============
    
    def create_combate(self, payload: dict, timeout=None) -> dict:
        """
        POST /apiCombates/combate
        Devuelve el JSON del combate creado (incluyendo su id).
        """
        r = self.post_json("/apiCombates/combate", payload, timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else {}

    def prepare_combate(self, combate_id: int, timeout=None) -> str:
        """
        POST /apiCombates/combate/{id}/prepare
        Prepara el registro de sockets (rojo/azul) para ese combate.
        """
        url = f"{self.base_url}/apiCombates/combate/{combate_id}/prepare"
        r = self.session.post(url, headers=self.headers(), timeout=timeout or self.timeout)
        if r.status_code == 404:
            raise RuntimeError(f"Combate {combate_id} no encontrado en el servidor.")
        r.raise_for_status()
        return r.text or "OK"

    def get_all_combates(self, timeout=None) -> list:
        """
        GET /apiCombates/combates
        Devuelve la lista de todos los combates.
        """
        r = self.get_json("/apiCombates/combates", timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else []

    def get_combate_by_id(self, combate_id: int, timeout=None) -> dict:
        """
        GET /apiCombates/combate/{id}
        Devuelve un combate específico por su ID.
        """
        r = self.get_json(f"/apiCombates/combate/{combate_id}", timeout=timeout)
        if r.status_code == 404:
            raise RuntimeError(f"Combate {combate_id} no encontrado.")
        r.raise_for_status()
        return r.json() if r.content else {}

    def get_combates_by_area(self, nombre_area: str, timeout=None) -> list:
        """
        GET /apiCombates/combates/area/{nombreArea}
        Devuelve combates filtrados por área.
        """
        r = self.get_json(f"/apiCombates/combates/area/{nombre_area}", timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else []

    def get_combates_by_estado(self, estado: str, timeout=None) -> list:
        """
        GET /apiCombates/combates/estado/{estado}
        Devuelve combates filtrados por estado.
        Ejemplo: estado = "FINALIZADO", "EN_CURSO", "PENDIENTE", "CANCELADO"
        """
        r = self.get_json(f"/apiCombates/combates/estado/{estado}", timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else []

    def update_combate(self, combate_id: int, payload: dict, timeout=None) -> dict:
        """
        PUT /apiCombates/combate/{id}
        Actualiza un combate existente.
        """
        r = self.put_json(f"/apiCombates/combate/{combate_id}", payload, timeout=timeout)
        if r.status_code == 404:
            raise RuntimeError(f"Combate {combate_id} no encontrado.")
        r.raise_for_status()
        return r.json() if r.content else {}

    def delete_combate(self, combate_id: int, timeout=None) -> bool:
        """
        DELETE /apiCombates/combate/{id}
        Elimina un combate por su ID.
        Devuelve True si se eliminó correctamente.
        """
        r = self.delete(f"/apiCombates/combate/{combate_id}", timeout=timeout)
        if r.status_code == 404:
            raise RuntimeError(f"Combate {combate_id} no encontrado.")
        r.raise_for_status()
        return r.status_code in (200, 204)

# Instancia global del cliente
api = ApiClient()