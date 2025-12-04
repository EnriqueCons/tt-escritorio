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
    
    def get_combates_by_torneo(self, torneo_id: int, timeout=None) -> list:
        """
        GET /apiCombates/combates/torneo/{idTorneo}
        Devuelve combates de un torneo específico.
        """
        r = self.get_json(f"/apiCombates/combates/torneo/{torneo_id}", timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else []
    
    # ============ ENDPOINTS DE TORNEOS ============
    
    def get_all_torneos(self, timeout=None) -> list:
        """
        GET /apiTorneos/torneo
        Devuelve la lista de todos los torneos.
        """
        r = self.get_json("/apiTorneos/torneo", timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else []

    def get_torneo_by_id(self, torneo_id: int, timeout=None) -> dict:
        """
        GET /apiTorneos/torneo/{id}
        Devuelve un torneo específico por su ID.
        """
        print(f"[DEBUG API] Obteniendo torneo {torneo_id}")
        
        r = self.get_json(f"/apiTorneos/torneo/{torneo_id}", timeout=timeout)
        
        print(f"[DEBUG API] Status code: {r.status_code}")
        
        if r.status_code == 404:
            raise RuntimeError(f"Torneo {torneo_id} no encontrado.")
        
        r.raise_for_status()
        
        result = r.json() if r.content else {}
        print(f"[DEBUG API] Torneo obtenido: {result}")
        
        return result

    def create_torneo(self, payload: dict, timeout=None) -> dict:
        """
        POST /apiTorneos/torneo
        Crea un nuevo torneo.
        Devuelve el JSON del torneo creado (incluyendo su id).
        """
        r = self.post_json("/apiTorneos/torneo", payload, timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else {}

    def update_torneo(self, torneo_id: int, payload: dict, timeout=None) -> dict:
        """
        PUT /apiTorneos/torneo/{id}
        Actualiza un torneo existente.
        """
        print(f"[DEBUG API] Actualizando torneo {torneo_id} con payload: {payload}")
        
        r = self.put_json(f"/apiTorneos/torneo/{torneo_id}", payload, timeout=timeout)
        
        print(f"[DEBUG API] Status code: {r.status_code}")
        print(f"[DEBUG API] Response text: {r.text}")
        
        if r.status_code == 404:
            raise RuntimeError(f"Torneo {torneo_id} no encontrado.")
        
        r.raise_for_status()
        
        result = r.json() if r.content else {}
        print(f"[DEBUG API] Response JSON: {result}")
        
        return result

    def delete_torneo(self, torneo_id: int, timeout=None) -> bool:
        """
        DELETE /apiTorneos/torneo/{id}
        Elimina un torneo por su ID.
        Devuelve True si se eliminó correctamente.
        """
        r = self.delete(f"/apiTorneos/torneo/{torneo_id}", timeout=timeout)
        if r.status_code == 404:
            raise RuntimeError(f"Torneo {torneo_id} no encontrado.")
        r.raise_for_status()
        return r.status_code in (200, 204)

    def get_ultimo_torneo(self, timeout=None) -> dict:
        """
        GET /apiTorneos/torneo/ultimo
        Obtiene el último torneo creado.
        """
        r = self.get_json("/apiTorneos/torneo/ultimo", timeout=timeout)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json() if r.content else None

    # ============ ENDPOINTS DE PUNTAJES ============
    
    def get_all_puntajes(self, timeout=None) -> list:
        """
        GET /apiPuntajes/puntaje
        Devuelve la lista de todos los puntajes.
        """
        r = self.get_json("/apiPuntajes/puntaje", timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else []

    def get_puntaje_by_id(self, puntaje_id: int, timeout=None) -> dict:
        """
        GET /apiPuntajes/puntaje/{id}
        Devuelve un puntaje específico por su ID.
        """
        r = self.get_json(f"/apiPuntajes/puntaje/{puntaje_id}", timeout=timeout)
        if r.status_code == 404:
            raise RuntimeError(f"Puntaje {puntaje_id} no encontrado.")
        r.raise_for_status()
        return r.json() if r.content else {}

    def create_puntaje(self, payload: dict, timeout=None) -> dict:
        """
        POST /apiPuntajes/puntaje
        Crea un nuevo registro de puntaje.
        """
        r = self.post_json("/apiPuntajes/puntaje", payload, timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else {}

    def update_puntaje(self, puntaje_id: int, payload: dict, timeout=None) -> dict:
        """
        PUT /apiPuntajes/puntaje/{id}
        Actualiza un puntaje existente.
        """
        r = self.put_json(f"/apiPuntajes/puntaje/{puntaje_id}", payload, timeout=timeout)
        if r.status_code == 404:
            raise RuntimeError(f"Puntaje {puntaje_id} no encontrado.")
        r.raise_for_status()
        return r.json() if r.content else {}

    def delete_puntaje(self, puntaje_id: int, timeout=None) -> bool:
        """
        DELETE /apiPuntajes/puntaje/{id}
        Elimina un puntaje por su ID.
        """
        r = self.delete(f"/apiPuntajes/puntaje/{puntaje_id}", timeout=timeout)
        if r.status_code == 404:
            raise RuntimeError(f"Puntaje {puntaje_id} no encontrado.")
        r.raise_for_status()
        return r.status_code in (200, 204)

    def get_puntaje_count(self, alumno_id: int, timeout=None) -> int:
        """
        GET /apiPuntajes/puntaje/alumno/{alumnoId}/count
        Obtiene el conteo de puntajes de un alumno.
        Retorna: {"alumnoId": X, "count": Y}
        Devuelve el valor de count (int).
        """
        try:
            r = self.get_json(f"/apiPuntajes/puntaje/alumno/{alumno_id}/count", timeout=timeout)
            if r.status_code == 404:
                return 0
            r.raise_for_status()
            data = r.json() if r.content else {}
            return int(data.get('count', 0))
        except Exception as e:
            print(f"[ApiClient] Error al obtener puntaje para alumno {alumno_id}: {e}")
            return 0
    
    # Agregar estos métodos a la clase ApiClient en api_client.py

    # ============ ENDPOINTS DE ADMINISTRADOR ============
    
    def get_all_administradores(self, timeout=None) -> list:
        """
        GET /apiAdministradores/administrador
        Devuelve la lista de todos los administradores.
        """
        r = self.get_json("/apiAdministradores/administrador", timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else []

    def get_administrador_by_id(self, admin_id: int, timeout=None) -> dict:
        """
        GET /apiAdministradores/administrador/{id}
        Devuelve un administrador específico por su ID.
        """
        print(f"[DEBUG API] Obteniendo administrador {admin_id}")
        
        r = self.get_json(f"/apiAdministradores/administrador/{admin_id}", timeout=timeout)
        
        print(f"[DEBUG API] Status code: {r.status_code}")
        
        if r.status_code == 404:
            raise RuntimeError(f"Administrador {admin_id} no encontrado.")
        
        r.raise_for_status()
        
        result = r.json() if r.content else {}
        print(f"[DEBUG API] Administrador obtenido: {result}")
        
        return result

    def create_administrador(self, payload: dict, timeout=None) -> dict:
        """
        POST /apiAdministradores/administrador
        Crea un nuevo administrador.
        """
        r = self.post_json("/apiAdministradores/administrador", payload, timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else {}

    def update_administrador(self, admin_id: int, payload: dict, timeout=None) -> dict:
        """
        PUT /apiAdministradores/administrador/{id}
        Actualiza un administrador existente.
        """
        print(f"[DEBUG API] Actualizando administrador {admin_id} con payload: {payload}")
        
        r = self.put_json(f"/apiAdministradores/administrador/{admin_id}", payload, timeout=timeout)
        
        print(f"[DEBUG API] Status code: {r.status_code}")
        print(f"[DEBUG API] Response text: {r.text}")
        
        if r.status_code == 404:
            raise RuntimeError(f"Administrador {admin_id} no encontrado.")
        
        r.raise_for_status()
        
        result = r.json() if r.content else {}
        print(f"[DEBUG API] Response JSON: {result}")
        
        return result

    def delete_administrador(self, admin_id: int, timeout=None) -> bool:
        """
        DELETE /apiAdministradores/administrador/{id}
        Elimina un administrador por su ID.
        """
        r = self.delete(f"/apiAdministradores/administrador/{admin_id}", timeout=timeout)
        if r.status_code == 404:
            raise RuntimeError(f"Administrador {admin_id} no encontrado.")
        r.raise_for_status()
        return r.status_code in (200, 204)

    def admin_login(self, login: str, password: str, timeout=None) -> dict:
        """
        POST /api/auth/admin/login
        Inicia sesión como administrador.
        Retorna: {"accessToken": "...", "tokenType": "Bearer", "expiresIn": 7200, "admin": {...}}
        """
        payload = {
            "login": login,
            "password": password
        }
        r = self.post_json("/api/auth/admin/login", payload, timeout=timeout)
        r.raise_for_status()
        return r.json() if r.content else {}

    def admin_logout(self, timeout=None):
        """
        POST /api/auth/admin/logout
        Cierra sesión del administrador.
        """
        return self.post_logout("/api/auth/admin/logout", timeout=timeout)
    
    def get_combate_by_id(self, combate_id):
        """
        Obtiene los datos completos de un combate por su ID
        GET /apiCombates/combate/{id}
        """
        url = f"{self.base_url}/apiCombates/combate/{combate_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error al obtener combate: {str(e)}")

# Instancia global del cliente
api = ApiClient()