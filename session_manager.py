class SessionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._admin_id = None
        self._admin_data = None
        self._access_token = None
    
    def set_session_from_app(self, app):
        """
        Establece la sesión desde el objeto app.auth
        que se configura en el login
        """
        if hasattr(app, 'auth') and app.auth:
            auth_data = app.auth
            admin = auth_data.get('admin', {})
            token = auth_data.get('access_token')
            
            self._admin_id = admin.get('idAdministrador')
            self._admin_data = admin
            self._access_token = token
            
            print(f"[SessionManager] Sesión establecida desde app para admin ID: {self._admin_id}")
            return True
        return False
    
    def set_session(self, admin_id: int, admin_data: dict, access_token: str = None):
        """Establece la sesión del administrador actual"""
        self._admin_id = admin_id
        self._admin_data = admin_data
        self._access_token = access_token
        print(f"[SessionManager] Sesión establecida para admin ID: {admin_id}")
    
    def get_admin_id(self) -> int:
        """Retorna el ID del administrador actual"""
        return self._admin_id
    
    def get_admin_data(self) -> dict:
        """Retorna los datos completos del administrador actual"""
        return self._admin_data
    
    def get_access_token(self) -> str:
        """Retorna el token de acceso"""
        return self._access_token
    
    def is_logged_in(self) -> bool:
        """Verifica si hay un administrador logueado"""
        return self._admin_id is not None
    
    def clear_session(self):
        """Limpia la sesión actual"""
        self._admin_id = None
        self._admin_data = None
        self._access_token = None
        print("[SessionManager] Sesión cerrada")
    
    def update_admin_data(self, updated_data: dict):
        """Actualiza los datos del administrador en la sesión"""
        if self._admin_data:
            self._admin_data.update(updated_data)
            print(f"[SessionManager] Datos actualizados para admin ID: {self._admin_id}")

# Instancia global
session = SessionManager()