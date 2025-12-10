from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.utils import get_color_from_hex, platform
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp
from kivy.core.window import Window
from threading import Thread
from kivy.clock import mainthread
import requests
import json

try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("=" * 60)
    print("  ADVERTENCIA: websocket-client no instalado")
    print("  Ejecuta: pip install websocket-client")
    print("  Las actualizaciones en tiempo real NO funcionarán")
    print("=" * 60)


# ------------------ UTILIDADES RESPONSIVE ------------------
class ResponsiveHelper:
    @staticmethod
    def is_mobile():
        return platform in ['android', 'ios']
    
    @staticmethod
    def is_desktop():
        return platform in ['win', 'linux', 'macosx']
    
    @staticmethod
    def get_font_size(base_size):
        width = Window.width
        height = Window.height
        min_dimension = min(width, height)
        
        if min_dimension < 600:
            return sp(base_size * 0.6)
        elif min_dimension < 900:
            return sp(base_size * 0.75)
        elif min_dimension < 1200:
            return sp(base_size * 0.9)
        return sp(base_size)
    
    @staticmethod
    def get_popup_size():
        width = Window.width
        height = Window.height
        if width < 600:
            return (width * 0.9, min(height * 0.4, dp(300)))
        else:
            return (min(width * 0.6, dp(450)), min(height * 0.35, dp(250)))
    
    @staticmethod
    def get_layout_orientation():
        return 'horizontal' if Window.width > Window.height and Window.width > 800 else 'vertical'
    
    @staticmethod
    def get_button_height():
        width = Window.width
        if width < 600:
            return dp(40)
        return dp(50)


# ------------------ PANEL DE COMPETIDOR CON WEBSOCKET ------------------
class CompetitorPanel(BoxLayout):
    score = NumericProperty(0)
    penalty_score = NumericProperty(0)
    api_score = NumericProperty(0)

    def __init__(self, name, color, nationality="", alumno_id=None, combate_id=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.name = name
        self.bg_color = get_color_from_hex(color)
        self.nationality = nationality
        self.alumno_id = alumno_id
        self.combate_id = combate_id
        self.parent_screen = None  # Referencia a MainScreentabc
        self.max_gamjeom = 3  # Máximo de faltas antes de descalificación
        
        self.build_ui()
        # Window.bind(on_resize=self.on_window_resize)

    def build_ui(self):
        self.clear_widgets()
        self.spacing = dp(10)
        self.padding = [dp(10), dp(15)]

        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

        # Nacionalidad
        if self.nationality:
            nationality_label = Label(
                text=self.nationality.upper(),
                font_size=ResponsiveHelper.get_font_size(18),
                bold=True,
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(30)
            )
            self.add_widget(nationality_label)

        # Nombre del competidor
        name_label = Label(
            text=self.name,
            font_size=ResponsiveHelper.get_font_size(28),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        self.add_widget(name_label)

        # Espaciador
        self.add_widget(BoxLayout(size_hint_y=0.1))

        # Puntuación principal
        score_layout = BoxLayout(
            size_hint_y=None,
            height=dp(80),
            spacing=dp(10),
            padding=[dp(5), 0]
        )
        
        btn_minus_score = Button(
            text="-",
            on_press=lambda x: self.subtract_score_api(),
            font_size=ResponsiveHelper.get_font_size(25),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        score_layout.add_widget(btn_minus_score)
        
        self.score_label = Label(
            text="0",
            font_size=ResponsiveHelper.get_font_size(50),
            color=(1, 1, 1, 1),
            bold=True
        )
        score_layout.add_widget(self.score_label)
        
        btn_plus_score = Button(
            text="+",
            on_press=lambda x: self.add_score_api(),
            font_size=ResponsiveHelper.get_font_size(25),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        score_layout.add_widget(btn_plus_score)
        
        self.add_widget(score_layout)

        # Indicador de estado (conexión, errores, etc.)
        self.status_indicator = Label(
            text="",
            font_size=ResponsiveHelper.get_font_size(12),
            color=(1, 1, 0.5, 1),
            size_hint_y=None,
            height=dp(20)
        )
        self.add_widget(self.status_indicator)

        # Espaciador
        self.add_widget(BoxLayout(size_hint_y=0.05))

        # Etiqueta GAM-JEOM
        gam_jeom_label = Label(
            text="GAM-JEOM",
            font_size=ResponsiveHelper.get_font_size(18),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(gam_jeom_label)

        # Penalizaciones GAM-JEOM
        penalty_layout = BoxLayout(
            size_hint_y=None,
            height=dp(70),
            spacing=dp(10),
            padding=[dp(5), 0]
        )
        
        btn_minus_penalty = Button(
            text="-",
            on_press=lambda x: self.subtract_gamjeom_api(),
            font_size=ResponsiveHelper.get_font_size(25),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        penalty_layout.add_widget(btn_minus_penalty)
        
        self.penalty_label = Label(
            text="0",
            font_size=ResponsiveHelper.get_font_size(35),
            color=(1, 1, 1, 1),
            bold=True
        )
        penalty_layout.add_widget(self.penalty_label)
        
        btn_plus_penalty = Button(
            text="+",
            on_press=lambda x: self.add_gamjeom_api(),
            font_size=ResponsiveHelper.get_font_size(25),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        penalty_layout.add_widget(btn_plus_penalty)
        
        self.add_widget(penalty_layout)

        # Indicador de estado GAM-JEOM
        self.gamjeom_status = Label(
            text="",
            font_size=ResponsiveHelper.get_font_size(12),
            color=(1, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(20)
        )
        self.add_widget(self.gamjeom_status)

        # Espaciador final
        self.add_widget(BoxLayout(size_hint_y=0.1))

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)

    # ==================== MÉTODOS DE PUNTAJE ====================

    def add_score_api(self):
        """ Suma 1 punto directamente en la BD (tiempo real) """
        if not self.alumno_id or not self.combate_id:
            print("[CompetitorPanel] No hay alumno_id o combate_id")
            return
    
        # Verificar si el timer está activo
        if self.parent_screen and not self.parent_screen.is_timer_active():
            self.show_status("Inicia el timer primero")
            print("[CompetitorPanel] Timer no activo, no se puede sumar")
            return
    
        self.show_status("Guardando...")
    
        def work():
            try:
                url = f"http://localhost:8080/apiPuntajes/puntaje/simple?combateId={self.combate_id}&alumnoId={self.alumno_id}&valorPuntaje=1"
                response = requests.post(url, timeout=5)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    print(f"[CompetitorPanel] +1 punto guardado para alumno {self.alumno_id}")
                    new_count = data.get('newCount', 0)
                    self.update_api_score(new_count)
                    self.show_status("+1")
                    Clock.schedule_once(lambda dt: self.clear_status(), 1)
                else:
                    print(f"[CompetitorPanel] ✗ Error al guardar: {response.status_code}")
                    self.show_status(f"✗ Error {response.status_code}")
            except Exception as e:
                print(f"[CompetitorPanel] ✗ Excepción: {e}")
                self.show_status("✗ Error conexión")
        
        Thread(target=work, daemon=True).start()

    def subtract_score_api(self):
        """Resta 1 punto (elimina el último registro de la BD)"""
        if not self.alumno_id:
            print("[CompetitorPanel] No hay alumno_id")
            return
        
        # Verificar si el timer está activo
        if self.parent_screen and not self.parent_screen.is_timer_active():
            self.show_status("Inicia el timer primero")
            print("[CompetitorPanel] Timer no activo, no se puede restar")
            return
        
        # No permitir restar si ya está en 0
        if self.api_score <= 0:
            self.show_status("Ya está en 0")
            return
        
        self.show_status("Eliminando...")
        
        def work():
            try:
                url = f"http://localhost:8080/apiPuntajes/puntaje/alumno/{self.alumno_id}/last"
                response = requests.delete(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    new_count = data.get('newCount', 0)
                    print(f"[CompetitorPanel] ✓ -1 punto eliminado para alumno {self.alumno_id}, nuevo total: {new_count}")
                    self.update_api_score(new_count)
                    self.show_status("-1")
                    Clock.schedule_once(lambda dt: self.clear_status(), 1)
                elif response.status_code == 204:
                    print(f"[CompetitorPanel] ✓ Punto eliminado")
                    self.refresh_score()
                    self.show_status("✓ -1")
                    Clock.schedule_once(lambda dt: self.clear_status(), 1)
                else:
                    print(f"[CompetitorPanel] ✗ Error al eliminar: {response.status_code}")
                    self.show_status(f"✗ Error {response.status_code}")
            except Exception as e:
                print(f"[CompetitorPanel] ✗ Excepción: {e}")
                self.show_status("✗ Error conexión")
        
        Thread(target=work, daemon=True).start()

    def refresh_score(self):
        """Refresca el puntaje desde la API"""
        if not self.alumno_id:
            return
        
        def work():
            try:
                url = f"http://localhost:8080/apiPuntajes/puntaje/alumno/{self.alumno_id}/count"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    new_count = response.json().get('count', 0)
                    self.update_api_score(new_count)
            except Exception as e:
                print(f"[CompetitorPanel] ✗ Error refrescando: {e}")
        
        Thread(target=work, daemon=True).start()

    @mainthread
    def update_api_score(self, new_score):
        """Actualiza el puntaje desde el WebSocket en tiempo real"""
        self.api_score = new_score
        self.score_label.text = str(self.api_score)
        print(f"[CompetitorPanel] 📊 Score actualizado: {self.name} = {self.api_score}")

    @mainthread
    def show_status(self, text):
        """Muestra un mensaje de estado temporal"""
        self.status_indicator.text = text
    
    @mainthread
    def clear_status(self):
        """Limpia el mensaje de estado"""
        self.status_indicator.text = ""

    # ==================== MÉTODOS DE GAM-JEOM ====================

    def add_gamjeom_api(self):
        """Suma 1 falta GAM-JEOM directamente en la BD"""
        if not self.alumno_id or not self.combate_id:
            print("[CompetitorPanel] No hay alumno_id o combate_id")
            return
        
        # Verificar si el timer está activo
        if self.parent_screen and not self.parent_screen.is_timer_active():
            self.show_gamjeom_status("Inicia el timer primero")
            print("[CompetitorPanel] Timer no activo, no se puede agregar falta")
            return
        
        self.show_gamjeom_status("Registrando falta...")
        
        def work():
            try:
                url = f"http://localhost:8080/apiGamJeom/falta/simple?combateId={self.combate_id}&alumnoId={self.alumno_id}"
                response = requests.post(url, timeout=5)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    total_faltas = data.get('totalFaltas', 0)
                    descalificado = data.get('descalificado', False)
                    
                    print(f"[CompetitorPanel] ⚠️ +1 falta registrada para alumno {self.alumno_id}, total: {total_faltas}")
                    self.update_gamjeom_count(total_faltas)
                    
                    if descalificado:
                        self.show_gamjeom_status("❌ DESCALIFICADO")
                        # Notificar al parent_screen para terminar el combate
                        if self.parent_screen:
                            self.parent_screen.on_player_disqualified(self.alumno_id, self.name)
                    else:
                        self.show_gamjeom_status(f"Falta {total_faltas}/3")
                        Clock.schedule_once(lambda dt: self.clear_gamjeom_status(), 2)
                else:
                    print(f"[CompetitorPanel] ✗ Error al registrar falta: {response.status_code}")
                    self.show_gamjeom_status(f"✗ Error {response.status_code}")
            except Exception as e:
                print(f"[CompetitorPanel] ✗ Excepción: {e}")
                self.show_gamjeom_status("✗ Error conexión")
        
        Thread(target=work, daemon=True).start()

    def subtract_gamjeom_api(self):
        """Resta 1 falta GAM-JEOM (elimina la última)"""
        if not self.alumno_id or not self.combate_id:
            print("[CompetitorPanel] No hay alumno_id o combate_id")
            return
        
        # Verificar si el timer está activo
        if self.parent_screen and not self.parent_screen.is_timer_active():
            self.show_gamjeom_status("Inicia el timer primero")
            return
        
        # No permitir restar si ya está en 0
        if self.penalty_score <= 0:
            self.show_gamjeom_status("Ya está en 0")
            return
        
        self.show_gamjeom_status("Eliminando falta...")
        
        def work():
            try:
                url = f"http://localhost:8080/apiGamJeom/falta/alumno/{self.alumno_id}/combate/{self.combate_id}/last"
                response = requests.delete(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    new_count = data.get('newCount', 0)
                    print(f"[CompetitorPanel] ✓ -1 falta eliminada para alumno {self.alumno_id}, nuevo total: {new_count}")
                    self.update_gamjeom_count(new_count)
                    self.show_gamjeom_status("Falta eliminada")
                    Clock.schedule_once(lambda dt: self.clear_gamjeom_status(), 1)
                else:
                    print(f"[CompetitorPanel] ✗ Error al eliminar falta: {response.status_code}")
                    self.show_gamjeom_status(f"✗ Error {response.status_code}")
            except Exception as e:
                print(f"[CompetitorPanel] ✗ Excepción: {e}")
                self.show_gamjeom_status("✗ Error conexión")
        
        Thread(target=work, daemon=True).start()

    def refresh_gamjeom(self):
        """Refresca el conteo de faltas desde la API"""
        if not self.alumno_id or not self.combate_id:
            return
        
        def work():
            try:
                url = f"http://localhost:8080/apiGamJeom/falta/alumno/{self.alumno_id}/combate/{self.combate_id}/count"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    new_count = data.get('count', 0)
                    self.update_gamjeom_count(new_count)
            except Exception as e:
                print(f"[CompetitorPanel] ✗ Error refrescando faltas: {e}")
        
        Thread(target=work, daemon=True).start()

    @mainthread
    def update_gamjeom_count(self, count):
        """Actualiza el contador visual de faltas"""
        self.penalty_score = count
        self.penalty_label.text = str(count)
        
        # Cambiar color si está cerca del límite
        if count >= 2:
            self.penalty_label.color = (1, 0.3, 0.3, 1)  # Rojo
        elif count >= 1:
            self.penalty_label.color = (1, 0.7, 0.3, 1)  # Naranja
        else:
            self.penalty_label.color = (1, 1, 1, 1)  # Blanco
        
        print(f"[CompetitorPanel] ⚠️ GAM-JEOM actualizado: {self.name} = {count}")

    @mainthread
    def show_gamjeom_status(self, text):
        """Muestra un mensaje de estado para GAM-JEOM"""
        self.gamjeom_status.text = text
    
    @mainthread
    def clear_gamjeom_status(self):
        """Limpia el mensaje de estado de GAM-JEOM"""
        self.gamjeom_status.text = ""

    def reset_scores(self):
        """Reinicia puntajes para nuevo round (solo visual, no toca BD)"""
        self.clear_status()
        self.clear_gamjeom_status()


# ------------------ PANEL CENTRAL CON CUENTA REGRESIVA ------------------
class CenterPanel(BoxLayout):
    time_str = StringProperty("03:00")
    round_str = StringProperty("Round 1")
    combat_started = BooleanProperty(False)

    def __init__(self, duracion_round=180, duracion_descanso=60, numero_rounds=3, **kwargs):
        super().__init__(**kwargs)
        self.timer_running = False
        self.round_number = 1
        self.numero_rounds = numero_rounds
        self.duracion_round = duracion_round
        self.duracion_descanso = duracion_descanso
        self.remaining_time = duracion_round
        self.is_rest_time = False
        
        self.build_ui()
        # Window.bind(on_resize=self.on_window_resize)

    def build_ui(self):
        self.clear_widgets()
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self.padding = [dp(15), dp(20)]

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Indicador de estado del combate
        self.combat_status_label = Label(
            text="COMBATE NO INICIADO",
            font_size=ResponsiveHelper.get_font_size(14),
            color=(0.8, 0.2, 0.2, 1),
            bold=True,
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(self.combat_status_label)

        # Ronda actual
        round_title = Label(
            text="RONDA ACTUAL",
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(round_title)
        
        self.round_label = Label(
            text=self.round_str,
            font_size=ResponsiveHelper.get_font_size(35),
            color=(0, 0, 0, 1),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.add_widget(self.round_label)

        # Espaciador
        self.add_widget(BoxLayout(size_hint_y=0.1))

        # Tiempo
        time_title = Label(
            text="TIEMPO",
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(time_title)
        
        self.time_label = Label(
            text=self.time_str,
            font_size=ResponsiveHelper.get_font_size(45),
            color=(0, 0, 0, 1),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        self.bind(time_str=self.time_label.setter('text'))
        self.add_widget(self.time_label)

        # Indicador de descanso
        self.rest_indicator = Label(
            text="",
            font_size=ResponsiveHelper.get_font_size(16),
            color=(1, 0.5, 0, 1),
            bold=True,
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(self.rest_indicator)

        # Espaciador
        self.add_widget(BoxLayout(size_hint_y=0.1))

        # Botones de control
        btn_layout = BoxLayout(
            size_hint_y=None,
            height=ResponsiveHelper.get_button_height(),
            spacing=dp(10)
        )
        
        btn_pause = Button(
            text="PAUSA",
            on_press=lambda x: self.pause_timer(),
            background_color=(0.1, 0.4, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=ResponsiveHelper.get_font_size(16),
            bold=True
        )
        btn_layout.add_widget(btn_pause)
        
        btn_play = Button(
            text="INICIAR",
            on_press=lambda x: self.start_timer(),
            background_color=(0.2, 0.7, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=ResponsiveHelper.get_font_size(16),
            bold=True
        )
        btn_layout.add_widget(btn_play)
        
        self.add_widget(btn_layout)

        # Espaciador
        self.add_widget(BoxLayout(size_hint_y=0.1))

        # Botón siguiente ronda
        self.next_round_button = Button(
            text="SIGUIENTE RONDA",
            size_hint_y=None,
            height=ResponsiveHelper.get_button_height(),
            background_color=(0.1, 0.4, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=ResponsiveHelper.get_font_size(16),
            bold=True,
            on_press=self.show_next_round_confirmation
        )
        self.add_widget(self.next_round_button)

        # Botón finalizar combate
        self.end_button = Button(
            text="FINALIZAR COMBATE",
            size_hint_y=None,
            height=ResponsiveHelper.get_button_height(),
            background_color=(0.1, 0.4, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=ResponsiveHelper.get_font_size(16),
            bold=True,
            on_press=self.show_end_combat_confirmation
        )
        self.add_widget(self.end_button)
        
        # Botón salir
        self.back_button = Button(
            text="SALIR",
            size_hint_y=None,
            height=ResponsiveHelper.get_button_height(),
            background_color=(0.7, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            font_size=ResponsiveHelper.get_font_size(16),
            bold=True,
            on_press=self.go_back
        )
        self.add_widget(self.back_button)

        # Espaciador final
        self.add_widget(BoxLayout(size_hint_y=0.1))

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)

    def start_timer(self):
        """Inicia el timer y marca el combate como activo"""
        if not self.timer_running:
            self.timer_running = True
            self.combat_started = True  
            self.combat_status_label.text = "COMBATE EN CURSO"
            self.combat_status_label.color = (0.2, 0.7, 0.2, 1)
            Clock.schedule_interval(self.update_time, 1)
            print("[CenterPanel] ⏱️ Timer iniciado - Combate ACTIVO")
            
            if hasattr(self, 'parent_screen') and self.parent_screen:
                self.parent_screen.on_combat_started()

    def pause_timer(self):
        """Pausa el timer pero el combate sigue activo"""
        self.timer_running = False
        Clock.unschedule(self.update_time)
        if self.combat_started:
            self.combat_status_label.text = "COMBATE PAUSADO"
            self.combat_status_label.color = (0.8, 0.6, 0, 1)
        print("[CenterPanel] ⏸️ Timer pausado")

    def is_combat_active(self):
        """Retorna True si el combate ha iniciado (aunque esté pausado)"""
        return self.combat_started

    def is_timer_running(self):
        """Retorna True si el timer está corriendo activamente"""
        return self.timer_running

    def update_time(self, dt):
        """Cuenta regresiva"""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.time_str = f"{minutes:02}:{seconds:02}"
        else:
            self.pause_timer()
            if self.is_rest_time:
                self.start_new_round()
            else:
                self.start_rest_period()

    def start_rest_period(self):
        """Inicia el período de descanso"""
        self.is_rest_time = True
        self.combat_started = False
        self.remaining_time = self.duracion_descanso
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_str = f"{minutes:02}:{seconds:02}"
        self.rest_indicator.text = "☕ DESCANSO"
        self.combat_status_label.text = "DESCANSO"
        self.combat_status_label.color = (0.8, 0.6, 0, 1)

    def start_new_round(self):
        """Inicia un nuevo round después del descanso"""

        if self.round_number >= self.numero_rounds:
            print(f"[CenterPanel] Todos los rounds completados ({self.numero_rounds})")
            self.end_combat_automatically()
            return
        
        # Incrementar el número de round
        self.round_number += 1
        self.round_str = f"Round {self.round_number}"
        self.round_label.text = self.round_str
        print(f"[CenterPanel] 🔄 Avanzando a Round {self.round_number}")
        
        # Resetear el estado del combate
        self.is_rest_time = False
        self.combat_started = False
        self.remaining_time = self.duracion_round
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_str = f"{minutes:02}:{seconds:02}"
        self.rest_indicator.text = ""
        
        # Actualizar estado visual
        self.combat_status_label.text = "✅ LISTO PARA INICIAR"
        self.combat_status_label.color = (0.8, 0.6, 0, 1)
        
        # Resetear los contadores visuales
        if hasattr(self, 'parent_screen') and self.parent_screen:
            self.parent_screen.reset_competitor_scores()
        
        
        # ✅ MANTENER PAUSADO: El usuario debe presionar INICIAR
        print(f"[CenterPanel] ⏸ Round {self.round_number} listo - Presiona INICIAR para comenzar")




    def end_combat_automatically(self):
        """Finaliza el combate automáticamente cuando se terminan todos los rounds"""
        self.pause_timer()
        self.combat_started = False
        self.is_rest_time = False
        self.time_str = "FIN"
        self.time_label.text = self.time_str
        self.round_label.text = "Combate Finalizado"
        self.rest_indicator.text = f"✅ {self.numero_rounds} rounds completados"
        self.combat_status_label.text = "COMBATE FINALIZADO"
        self.combat_status_label.color = (0.5, 0.5, 0.5, 1)
        
        print(f"[CenterPanel] 🏁 Combate finalizado automáticamente - {self.numero_rounds} rounds completados")
        
        # Mostrar mensaje al usuario
        self.mostrar_mensaje(
            titulo="Combate Finalizado",
            mensaje=f"Se han completado los {self.numero_rounds} rounds\n\nEl combate ha finalizado"
        )

    def end_combat_by_disqualification(self, player_name):
        """Termina el combate por descalificación (3 GAM-JEOM)"""
        self.pause_timer()
        self.combat_started = False
        self.time_str = "FIN"
        self.time_label.text = self.time_str
        self.round_label.text = "DESCALIFICACIÓN"
        self.rest_indicator.text = f"❌ {player_name}"
        self.combat_status_label.text = "⛔ COMBATE TERMINADO"
        self.combat_status_label.color = (0.8, 0.2, 0.2, 1)

    def mostrar_mensaje(self, titulo, mensaje, confirm_callback=None):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        lbl_mensaje = Label(
            text=mensaje,
            color=(0.1, 0.4, 0.7, 1),
            font_size=ResponsiveHelper.get_font_size(18),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80)
        )
        lbl_mensaje.bind(size=lbl_mensaje.setter('text_size'))
        content.add_widget(lbl_mensaje)
        
        btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=ResponsiveHelper.get_button_height())
        
        popup_size = ResponsiveHelper.get_popup_size()
        popup = Popup(
            title=titulo,
            title_color=(1, 1, 1, 1),
            title_size=ResponsiveHelper.get_font_size(22),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=popup_size,
            separator_height=0,
            background=''
        )
        
        if confirm_callback:
            btn_cancelar = Button(
                text='CANCELAR',
                size_hint_x=0.5,
                background_normal='',
                background_color=(0.8, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                bold=True,
                font_size=ResponsiveHelper.get_font_size(16)
            )
            btn_cancelar.bind(on_press=popup.dismiss)
            btn_layout.add_widget(btn_cancelar)
        
        btn_text = 'ACEPTAR' if confirm_callback else 'ENTENDIDO'
        btn_aceptar = Button(
            text=btn_text,
            size_hint_x=0.5 if confirm_callback else 1,
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(16)
        )
        
        if confirm_callback:
            btn_aceptar.bind(on_press=lambda x: [popup.dismiss(), confirm_callback()])
        else:
            btn_aceptar.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(btn_aceptar)
        content.add_widget(btn_layout)
        
        with popup.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            popup.rect = RoundedRectangle(pos=popup.pos, size=popup.size, radius=[dp(15)])
        
        def update_popup_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
        
        popup.bind(pos=update_popup_rect, size=update_popup_rect)
        popup.open()

    def show_next_round_confirmation(self, instance):
        if self.round_number >= self.numero_rounds:
            self.mostrar_mensaje(
                titulo="Máximo de Rondas",
                mensaje=f"Ya estás en la ronda {self.numero_rounds}\n(última ronda configurada)"
            )
            return
            
        self.mostrar_mensaje(
            titulo="Confirmar Siguiente Ronda",
            mensaje="¿Estás seguro de avanzar\na la siguiente ronda?",
            confirm_callback=lambda: self.next_round(instance)
        )

    def show_end_combat_confirmation(self, instance):
        self.mostrar_mensaje(
            titulo="Finalizar Combate",
            mensaje="¿Confirmas que deseas\nfinalizar el combate?",
            confirm_callback=lambda: self.end_combat(instance)
        )

    def next_round(self, instance):
        self.round_number += 1
        self.round_str = f"Round {self.round_number}"
        self.round_label.text = self.round_str
        self.remaining_time = self.duracion_round
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_str = f"{minutes:02}:{seconds:02}"
        self.is_rest_time = False
        self.rest_indicator.text = ""
        self.pause_timer()
        
        if hasattr(self, 'parent_screen'):
            self.parent_screen.reset_competitor_scores()
        
        self.mostrar_mensaje(
            titulo="Ronda Actualizada",
            mensaje=f"Has avanzado a la\nronda {self.round_number}"
        )

    def end_combat(self, instance):
        self.pause_timer()
        self.combat_started = False
        self.time_str = "FIN"
        self.time_label.text = self.time_str
        self.round_label.text = "Combate Finalizado"
        self.rest_indicator.text = ""
        self.combat_status_label.text = "COMBATE FINALIZADO"
        self.combat_status_label.color = (0.5, 0.5, 0.5, 1)
        self.mostrar_mensaje(
            titulo="Combate Finalizado",
            mensaje="El combate ha sido\ndado por finalizado"
        )
        
    def go_back(self, instance):
        self.mostrar_mensaje(
            titulo="Confirmar salida",
            mensaje="¿Estás segura(o) que deseas salir\nde este combate?",
            confirm_callback=self.confirm_go_back
        )

    def confirm_go_back(self):
        self.parent.parent.parent.current = 'ini'


# ------------------ PANTALLA PRINCIPAL CON WEBSOCKET ------------------
class MainScreentabc(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'tablero_central'
        self.combate_id = None
        self.id_alumno_rojo = None
        self.id_alumno_azul = None
        self.ws = None
        self.ws_thread = None
        self.ws_keepalive = None
        
        self.build_ui()
    
    def set_competitors(self, name1, nat1, name2, nat2, combate_data=None):
        """Configura los competidores y datos del combate"""
        print("\n" + "=" * 60)
        print("[MainScreentabc] 🥋 CONFIGURANDO COMPETIDORES")
        print(f"  🔵 Azul: {name2} ({nat2})")
        print(f"  🔴 Rojo: {name1} ({nat1})")
        
        if combate_data:
            self.combate_id = combate_data.get('idCombate') or combate_data.get('id')
            self.id_alumno_rojo = combate_data.get('idAlumnoRojo')
            self.id_alumno_azul = combate_data.get('idAlumnoAzul')
            
            duracion_round = self.parse_time_to_seconds(
                combate_data.get('duracionRound', '00:03:00')
            )
            duracion_descanso = self.parse_time_to_seconds(
                combate_data.get('duracionDescanso', '00:01:00')
            )
            numero_rounds = combate_data.get('numeroRounds', 3)
            
            print(f"\n[MainScreentabc] 📋 DATOS DEL COMBATE:")
            print(f"  ID Combate: {self.combate_id}")
            print(f"  ID Alumno Rojo: {self.id_alumno_rojo}")
            print(f"  ID Alumno Azul: {self.id_alumno_azul}")
            print(f"  Duración Round: {duracion_round}s")
            print(f"  Duración Descanso: {duracion_descanso}s")
            print(f"  Número Rounds: {numero_rounds}")
            print("=" * 60 + "\n")
        else:
            duracion_round = 180
            duracion_descanso = 60
            numero_rounds = 3
        
        self.rebuild_with_data(
            name1, nat1, name2, nat2,
            duracion_round, duracion_descanso, numero_rounds
        )
        
        # Conectar al WebSocket para actualizaciones en tiempo real
        if self.combate_id and WEBSOCKET_AVAILABLE:
            self.connect_websocket()
        elif not WEBSOCKET_AVAILABLE:
            print("⚠️ WebSocket no disponible - instala websocket-client")
    
    def parse_time_to_seconds(self, time_str):
        """Convierte HH:MM:SS a segundos totales"""
        try:
            parts = time_str.split(':')
            hours = int(parts[0]) if len(parts) > 0 else 0
            minutes = int(parts[1]) if len(parts) > 1 else 0
            seconds = int(parts[2]) if len(parts) > 2 else 0
            return hours * 3600 + minutes * 60 + seconds
        except Exception as e:
            print(f"[MainScreentabc] ✗ Error parseando tiempo '{time_str}': {e}")
            return 180
    
    def rebuild_with_data(self, name1, nat1, name2, nat2, 
                          duracion_round, duracion_descanso, numero_rounds):
        """Reconstruye la UI con los datos del combate"""
        self.clear_widgets()
        
        orientation = ResponsiveHelper.get_layout_orientation()
        main_layout = BoxLayout(orientation=orientation, spacing=0)
        
        # Panel Competidor Azul (IZQUIERDA)
        self.com2_panel = CompetitorPanel(
            name=name2,
            color="#1E88E5",
            nationality=nat2,
            alumno_id=self.id_alumno_azul,
            combate_id=self.combate_id
        )
        self.com2_panel.parent_screen = self
        main_layout.add_widget(self.com2_panel)

        # Panel Central
        self.center_panel = CenterPanel(
            duracion_round=duracion_round,
            duracion_descanso=duracion_descanso,
            numero_rounds=numero_rounds
        )
        self.center_panel.parent_screen = self
        main_layout.add_widget(self.center_panel)

        # Panel Competidor Rojo (DERECHA)
        self.com1_panel = CompetitorPanel(
            name=name1,
            color="#E53935",
            nationality=nat1,
            alumno_id=self.id_alumno_rojo,
            combate_id=self.combate_id
        )
        self.com1_panel.parent_screen = self
        main_layout.add_widget(self.com1_panel)

        self.add_widget(main_layout)
    
    def is_timer_active(self):
        """Verifica si el combate ha iniciado (timer activo) y NO está en descanso"""
        if hasattr(self, 'center_panel') and self.center_panel:
            return self.center_panel.is_combat_active() and not self.center_panel.is_rest_time
        return False
    
    def on_combat_started(self):
        """Callback cuando el combate inicia"""
        print("[MainScreentabc] 🟢 Combate iniciado - Puntos y faltas ahora serán aceptados")
        self.fetch_initial_gamjeom()

    def on_player_disqualified(self, alumno_id, player_name):
        """Callback cuando un jugador es descalificado por 3 GAM-JEOM"""
        print(f"\n{'='*60}")
        print(f"❌ DESCALIFICACIÓN: {player_name} (ID: {alumno_id})")
        print(f"   Ha acumulado 3 GAM-JEOM")
        print(f"{'='*60}\n")
        
        # Determinar el ganador
        if alumno_id == self.id_alumno_rojo:
            winner = self.com2_panel.name
        else:
            winner = self.com1_panel.name
        
        # Terminar el combate
        self.center_panel.end_combat_by_disqualification(player_name)
        
        # Mostrar mensaje
        self.center_panel.mostrar_mensaje(
            titulo="❌ DESCALIFICACIÓN",
            mensaje=f"{player_name} ha sido descalificado\npor acumular 3 faltas GAM-JEOM.\n\n🏆 Ganador: {winner}"
        )
    
    def connect_websocket(self):
        """Conecta al WebSocket del tablero para recibir actualizaciones en tiempo real"""
        if not WEBSOCKET_AVAILABLE:
            print("[MainScreentabc] ✗ WebSocket no disponible")
            return
    
        def on_message(ws, message):
            try:
                data = json.loads(message)
                print(f"[WebSocket] 📨 Mensaje recibido: {data}")
                
                if data.get('event') == 'score_update':
                    alumno_id = data.get('alumnoId')
                    new_count = data.get('count', 0)
                    
                    if not self.is_timer_active():
                        print(f"[WebSocket] ⚠️ Timer NO activo - Eliminando punto de alumno {alumno_id}")
                        self.revert_score(alumno_id)
                        return
                
                    if alumno_id == self.id_alumno_rojo:
                        print(f"[WebSocket] 🔴 Actualizando ROJO: {new_count}")
                        self.com1_panel.update_api_score(new_count)
                    elif alumno_id == self.id_alumno_azul:
                        print(f"[WebSocket] 🔵 Actualizando AZUL: {new_count}")
                        self.com2_panel.update_api_score(new_count)
                
                elif data.get('status') == 'connected':
                    print(f"[WebSocket] ✓ Conectado al combate {data.get('combateId')}")
                    self.fetch_initial_scores()
                    
            except Exception as e:
                print(f"[WebSocket] ✗ Error procesando mensaje: {e}")
    
        def on_error(ws, error):
            print(f"[WebSocket] ✗ Error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print(f"[WebSocket] ✗ Conexión cerrada: {close_status_code} - {close_msg}")
            if self.ws_keepalive:
                Clock.schedule_once(lambda dt: self.reconnect_websocket(), 3)
        
        def on_open(ws):
            print(f"[WebSocket] ✓ Conexión establecida al combate {self.combate_id}")
            self.start_keepalive()
        
        ws_url = f"ws://localhost:8080/ws/tablero/{self.combate_id}"
        print(f"\n[MainScreentabc] 🔌 Conectando a WebSocket: {ws_url}")
        
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        self.ws_thread = Thread(target=self.ws.run_forever, daemon=True)
        self.ws_thread.start()

        def on_error(ws, error):
            print(f"[WebSocket] ✗ Error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print(f"[WebSocket] ✗ Conexión cerrada: {close_status_code} - {close_msg}")
            if self.ws_keepalive:
                Clock.schedule_once(lambda dt: self.reconnect_websocket(), 3)
        
        def on_open(ws):
            print(f"[WebSocket] ✓ Conexión establecida al combate {self.combate_id}")
            self.start_keepalive()
        
        ws_url = f"ws://localhost:8080/ws/tablero/{self.combate_id}"
        print(f"\n[MainScreentabc] 🔌 Conectando a WebSocket: {ws_url}")
        
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        self.ws_thread = Thread(target=self.ws.run_forever, daemon=True)
        self.ws_thread.start()
    
    def revert_score(self, alumno_id):
        """Revierte (elimina) el último punto de un alumno cuando el timer no está activo"""
        def work():
            try:
                url = f"http://localhost:8080/apiPuntajes/puntaje/alumno/{alumno_id}/last"
                response = requests.delete(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"[MainScreentabc] ✓ Punto revertido para alumno {alumno_id}, nuevo count: {data.get('newCount', 0)}")
                elif response.status_code == 204:
                    print(f"[MainScreentabc] ✓ Punto revertido para alumno {alumno_id}")
                else:
                    print(f"[MainScreentabc] ⚠️ No se pudo revertir: {response.status_code}")
            except Exception as e:
                print(f"[MainScreentabc] ✗ Error revirtiendo punto: {e}")
        
        Thread(target=work, daemon=True).start()
    
    def start_keepalive(self):
        """Envía ping cada 30 segundos para mantener vivo el WebSocket"""
        def send_ping(dt):
            if self.ws and self.ws.sock and self.ws.sock.connected:
                try:
                    self.ws.send('ping')
                    print("[WebSocket] 💓 Keepalive ping enviado")
                except Exception as e:
                    print(f"[WebSocket] ✗ Error en keepalive: {e}")
        
        if self.ws_keepalive:
            self.ws_keepalive.cancel()
        
        self.ws_keepalive = Clock.schedule_interval(send_ping, 30)
        print("[WebSocket] ✓ Keepalive iniciado (ping cada 30s)")
    
    def reconnect_websocket(self):
        """Intenta reconectar el WebSocket"""
        if self.combate_id and WEBSOCKET_AVAILABLE:
            print("[WebSocket] 🔄 Intentando reconectar...")
            self.connect_websocket()

    @mainthread
    def update_judges_status(self, text):
        """Actualiza el estado de los jueces en el centro del tablero"""
        if hasattr(self, 'center_panel') and self.center_panel:
            print(f"[MainScreentabc] 👨‍⚖️ {text}")
            # Mostrar popup temporal con el estado de los jueces
            self.center_panel.mostrar_mensaje(
                titulo="Estado de Jueces",
                mensaje=text
            )
    
    def fetch_initial_scores(self):
        """Obtiene los puntajes iniciales al conectarse"""
        def work():
            try:
                if self.id_alumno_rojo:
                    url_rojo = f"http://localhost:8080/apiPuntajes/puntaje/alumno/{self.id_alumno_rojo}/count"
                    response_rojo = requests.get(url_rojo, timeout=2)
                    if response_rojo.status_code == 200:
                        count_rojo = response_rojo.json().get('count', 0)
                        self.com1_panel.update_api_score(count_rojo)
                        print(f"[MainScreentabc] 🔴 Puntaje inicial ROJO: {count_rojo}")
                
                if self.id_alumno_azul:
                    url_azul = f"http://localhost:8080/apiPuntajes/puntaje/alumno/{self.id_alumno_azul}/count"
                    response_azul = requests.get(url_azul, timeout=2)
                    if response_azul.status_code == 200:
                        count_azul = response_azul.json().get('count', 0)
                        self.com2_panel.update_api_score(count_azul)
                        print(f"[MainScreentabc] 🔵 Puntaje inicial AZUL: {count_azul}")
                
                print("[MainScreentabc] ✅ Puntajes iniciales cargados\n")
                
            except Exception as e:
                print(f"[MainScreentabc] ✗ Error obteniendo puntajes iniciales: {e}")
        
        Thread(target=work, daemon=True).start()

    def fetch_initial_gamjeom(self):
        """Obtiene las faltas GAM-JEOM iniciales al conectarse"""
        def work():
            try:
                if self.id_alumno_rojo and self.combate_id:
                    url_rojo = f"http://localhost:8080/apiGamJeom/falta/alumno/{self.id_alumno_rojo}/combate/{self.combate_id}/count"
                    response_rojo = requests.get(url_rojo, timeout=2)
                    if response_rojo.status_code == 200:
                        count_rojo = response_rojo.json().get('count', 0)
                        self.com1_panel.update_gamjeom_count(count_rojo)
                        print(f"[MainScreentabc] 🔴 GAM-JEOM inicial ROJO: {count_rojo}")
                
                if self.id_alumno_azul and self.combate_id:
                    url_azul = f"http://localhost:8080/apiGamJeom/falta/alumno/{self.id_alumno_azul}/combate/{self.combate_id}/count"
                    response_azul = requests.get(url_azul, timeout=2)
                    if response_azul.status_code == 200:
                        count_azul = response_azul.json().get('count', 0)
                        self.com2_panel.update_gamjeom_count(count_azul)
                        print(f"[MainScreentabc] 🔵 GAM-JEOM inicial AZUL: {count_azul}")
                
                print("[MainScreentabc] ✅ GAM-JEOM iniciales cargados\n")
                
            except Exception as e:
                print(f"[MainScreentabc] ✗ Error obteniendo GAM-JEOM iniciales: {e}")
        
        Thread(target=work, daemon=True).start()
    
    # ✅ NUEVO: Métodos para manejo de incidencias
    def pausar_tiempo(self):
        """Pausa el cronómetro cuando hay incidencia confirmada"""
        if hasattr(self, 'center_panel') and self.center_panel:
            self.center_panel.pause_timer()
            print("[MainScreentabc] ⏸️ Tiempo pausado por incidencia confirmada")

    def mostrar_popup_incidencia(self):
        """Muestra popup de incidencia confirmada"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(30)
        )

        lbl_mensaje = Label(
            text="🚨 INCIDENCIA REPORTADA 🚨\n\n2 o más jueces confirmaron\nuna incidencia",
            color=(1, 1, 1, 1),
            font_size=sp(26),
            halign='center',
            valign='middle',
            bold=True,
            size_hint_y=None,
            height=dp(150)
        )
        lbl_mensaje.bind(size=lbl_mensaje.setter('text_size'))
        content.add_widget(lbl_mensaje)

        btn_continuar = Button(
            text='CONTINUAR',
            background_normal='',
            background_color=(1, 0.8, 0, 1),
            color=(0, 0, 0, 1),
            bold=True,
            font_size=sp(22),
            size_hint_y=None,
            height=dp(70)
        )
        content.add_widget(btn_continuar)

        popup = Popup(
            title="⚠️ INCIDENCIA ⚠️",
            title_color=(1, 1, 0, 1),
            title_size=sp(28),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=(dp(600), dp(400)),
            separator_height=0,
            background='',
            auto_dismiss=False
        )

        with popup.canvas.before:
            Color(0.8, 0.1, 0.1, 0.95)  # Rojo para llamar la atención
            popup.rect = RoundedRectangle(
                pos=popup.pos,
                size=popup.size,
                radius=[dp(15)]
            )

        def update_popup_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

        popup.bind(pos=update_popup_rect, size=update_popup_rect)
        
        def continuar_combate(instance):
            popup.dismiss()
            # El operador puede reanudar manualmente con el botón INICIAR
        
        btn_continuar.bind(on_press=continuar_combate)
        popup.open()
        
        print("[MainScreentabc] 🚨 Popup de incidencia mostrado")

    def reanudar_tiempo(self):
        """Reanuda el cronómetro (opcional)"""
        if hasattr(self, 'center_panel') and self.center_panel:
            self.center_panel.start_timer()
            print("[MainScreentabc] ▶️ Tiempo reanudado")
    
    def disconnect_websocket(self):
        """Desconecta el WebSocket"""
        if self.ws_keepalive:
            self.ws_keepalive.cancel()
            self.ws_keepalive = None
        
        if self.ws:
            try:
                self.ws.close()
                print("[MainScreentabc] ✓ WebSocket desconectado")
            except Exception as e:
                print(f"[MainScreentabc] ✗ Error al desconectar WebSocket: {e}")
    
    def reset_competitor_scores(self):
        """Reinicia los contadores visuales para nuevo round"""
        self.com1_panel.reset_scores()
        self.com2_panel.reset_scores()
        
    def build_ui(self):
        """Construye la UI inicial (sin datos)"""
        self.clear_widgets()
        
        orientation = ResponsiveHelper.get_layout_orientation()
        main_layout = BoxLayout(orientation=orientation, spacing=0)
        
        # Panel Azul a la IZQUIERDA
        self.com2_panel = CompetitorPanel(
            name="COMPETIDOR 2",
            color="#1E88E5",
            nationality=""
        )
        self.com2_panel.parent_screen = self
        main_layout.add_widget(self.com2_panel)

        self.center_panel = CenterPanel()
        self.center_panel.parent_screen = self
        main_layout.add_widget(self.center_panel)

        # Panel Rojo a la DERECHA
        self.com1_panel = CompetitorPanel(
            name="COMPETIDOR 1",
            color="#E53935",
            nationality=""
        )
        self.com1_panel.parent_screen = self
        main_layout.add_widget(self.com1_panel)

        self.add_widget(main_layout)

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)

    def pausar_tiempo(self):
        """Pausa el cronómetro cuando hay incidencia confirmada"""
        if hasattr(self, 'center_panel') and self.center_panel:
            self.center_panel.pause_timer()
            print("[MainScreentabc] ⏸️ Tiempo pausado por incidencia confirmada")

    def mostrar_popup_incidencia(self):
        """Muestra popup de incidencia confirmada"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(25),
            padding=dp(40)
        )

        # Emoji grande arriba
        emoji_label = Label(
            text="🚨",
            font_size=sp(60),
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(emoji_label)

        # Mensaje principal más compacto
        lbl_mensaje = Label(
            text="INCIDENCIA REPORTADA",
            color=(0, 0, 0, 1),  
            font_size=sp(28),
            halign='center',
            valign='middle',
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        lbl_mensaje.bind(size=lbl_mensaje.setter('text_size'))
        content.add_widget(lbl_mensaje)

        # Submensaje
        lbl_sub = Label(
            text="2 o más jueces confirmaron\nuna incidencia",
            color=(0.2, 0.2, 0.2, 1),
            font_size=sp(18),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(60)
        )
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        content.add_widget(lbl_sub)

        # Espaciador
        content.add_widget(BoxLayout(size_hint_y=0.2))

        # Botón amarillo con texto negro
        btn_continuar = Button(
            text='CONTINUAR',
            background_normal='',
            background_color=(1, 0.8, 0, 1),  
            color=(0, 0, 0, 1),  
            bold=True,
            font_size=sp(22),
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(btn_continuar)

        popup = Popup(
            title=" ALERTA ",
            title_color=(0, 0, 0, 1), 
            title_size=sp(26),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=(dp(500), dp(450)), 
            separator_height=0,
            background='',
            auto_dismiss=False
        )

        # Fondo amarillo (más suave que rojo)
        with popup.canvas.before:
            Color(1, 0.9, 0.3, 0.98)  # ✅ Amarillo suave
            popup.rect = RoundedRectangle(
                pos=popup.pos,
                size=popup.size,
                radius=[dp(15)]
            )

        def update_popup_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

        popup.bind(pos=update_popup_rect, size=update_popup_rect)
        
        def continuar_combate(instance):
            popup.dismiss()
            # El operador puede reanudar manualmente con el botón INICIAR
        
        btn_continuar.bind(on_press=continuar_combate)
        popup.open()
        
        print("[MainScreentabc] Popup de incidencia mostrado")

    def reanudar_tiempo(self):
        """Reanuda el cronómetro (opcional)"""
        if hasattr(self, 'center_panel') and self.center_panel:
            self.center_panel.start_timer()
            print("[MainScreentabc] Tiempo reanudado")

    
    def on_pre_leave(self, *args):
        """Se ejecuta cuando se sale de esta pantalla"""
        print("[MainScreentabc] Saliendo del tablero, desconectando WebSocket...")
        self.disconnect_websocket()
        return super().on_pre_leave(*args)


# ------------------ APP DE PRUEBA ------------------
if __name__ == '__main__':
    class TestApp(App):
        def build(self):
            sm = ScreenManager()
            
            tablero = MainScreentabc(name='tablero_central')
            sm.add_widget(tablero)
            
            def simulate_combat_creation(dt):
                print("\n" + "=" * 60)
                print("SIMULACIÓN DE COMBATE")
                print("=" * 60)
                
                combate_data = {
                    'idCombate': 1,
                    'id': 1,
                    'idAlumnoRojo': 1,
                    'idAlumnoAzul': 2,
                    'duracionRound': '00:01:00',
                    'duracionDescanso': '00:00:30',
                    'numeroRounds': 3
                }
                
                tablero.set_competitors(
                    name1="Juan Pérez",
                    nat1="MEX",
                    name2="Kim Min-ho",
                    nat2="KOR",
                    combate_data=combate_data
                )
                
                print("\n✅ TABLERO CONFIGURADO")
                print("  🔵 AZUL (Kim Min-ho) - IZQUIERDA")
                print("  🔴 ROJO (Juan Pérez) - DERECHA")
                print("  IMPORTANTE: Debes presionar INICIAR para que cuenten los puntos")
                print("📡 Los puntajes se actualizan en tiempo real via WebSocket")
                print("🚨 2+ jueces marcan incidencia → POPUP + PAUSA AUTOMÁTICA")
                print("⚠️ 3 faltas GAM-JEOM = DESCALIFICACIÓN")
                print("=" * 60 + "\n")
            
            Clock.schedule_once(simulate_combat_creation, 2)
            
            return sm
    
    TestApp().run()