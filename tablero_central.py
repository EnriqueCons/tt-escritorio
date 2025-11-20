from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import NumericProperty, StringProperty
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
    print("⚠️  ADVERTENCIA: websocket-client no instalado")
    print("   Ejecuta: pip install websocket-client")
    print("   Las actualizaciones en tiempo real NO funcionarán")
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
    manual_score = NumericProperty(0)

    def __init__(self, name, color, nationality="", alumno_id=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.name = name
        self.bg_color = get_color_from_hex(color)
        self.nationality = nationality
        self.alumno_id = alumno_id
        self.api_score = 0  # Puntaje desde el backend
        
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

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
            on_press=lambda x: self.update_manual_score(-1),
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
            on_press=lambda x: self.update_manual_score(1),
            font_size=ResponsiveHelper.get_font_size(25),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        score_layout.add_widget(btn_plus_score)
        
        self.add_widget(score_layout)

        # Indicador de puntos manuales pendientes
        self.manual_indicator = Label(
            text="",
            font_size=ResponsiveHelper.get_font_size(14),
            color=(1, 1, 0.5, 1),
            size_hint_y=None,
            height=dp(20)
        )
        self.add_widget(self.manual_indicator)

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

        # Penalizaciones
        penalty_layout = BoxLayout(
            size_hint_y=None,
            height=dp(70),
            spacing=dp(10),
            padding=[dp(5), 0]
        )
        
        btn_minus_penalty = Button(
            text="-",
            on_press=lambda x: self.update_penalty(-1),
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
            on_press=lambda x: self.update_penalty(1),
            font_size=ResponsiveHelper.get_font_size(25),
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        penalty_layout.add_widget(btn_plus_penalty)
        
        self.add_widget(penalty_layout)

        # Espaciador final
        self.add_widget(BoxLayout(size_hint_y=0.1))

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)

    def update_penalty(self, value):
        self.penalty_score += value
        if self.penalty_score < 0:
            self.penalty_score = 0
        self.penalty_label.text = str(self.penalty_score)

    def update_manual_score(self, value):
        """Actualiza el puntaje manual (temporal, no guardado)"""
        self.manual_score += value
        if self.manual_score < 0:
            self.manual_score = 0
        
        # Actualizar display total
        total = self.api_score + self.manual_score
        self.score_label.text = str(total)
        
        # Mostrar indicador
        if self.manual_score > 0:
            self.manual_indicator.text = f"(+{self.manual_score} pendiente)"
        else:
            self.manual_indicator.text = ""

    @mainthread
    def update_api_score(self, new_score):
        """⭐ Actualiza el puntaje desde el WebSocket en tiempo real"""
        self.api_score = new_score
        total = self.api_score + self.manual_score
        self.score_label.text = str(total)
        print(f"[CompetitorPanel] 📊 Score actualizado: {self.name} = {total} (API: {self.api_score}, Manual: {self.manual_score})")

    def save_manual_scores(self, combate_id):
        """Guarda los puntos manuales al backend"""
        if self.manual_score <= 0:
            return True
        
        try:
            url = "http://localhost:8080/apiPuntajeDetalle/"
            payload = {
                "combate": {"idCombate": combate_id},
                "alumno": {"idAlumno": self.alumno_id},
                "valorPuntaje": self.manual_score
            }
            response = requests.post(url, json=payload, timeout=5)
            
            if response.status_code in [200, 201]:
                print(f"[CompetitorPanel] ✓ Puntos manuales guardados: {self.manual_score}")
                self.manual_score = 0
                self.manual_indicator.text = ""
                return True
            else:
                print(f"[CompetitorPanel] ✗ Error al guardar: {response.status_code}")
                return False
        except Exception as e:
            print(f"[CompetitorPanel] ✗ Excepción: {e}")
            return False

    def reset_scores(self):
        """Reinicia puntajes manuales para nuevo round"""
        self.manual_score = 0
        self.manual_indicator.text = ""


# ------------------ PANEL CENTRAL CON CUENTA REGRESIVA ------------------
class CenterPanel(BoxLayout):
    time_str = StringProperty("03:00")
    round_str = StringProperty("Round 1")

    def __init__(self, duracion_round=180, duracion_descanso=60, numero_rounds=3, **kwargs):
        super().__init__(**kwargs)
        self.timer_running = False
        self.round_number = 1
        self.numero_rounds = numero_rounds
        self.duracion_round = duracion_round  # en segundos
        self.duracion_descanso = duracion_descanso  # en segundos
        self.remaining_time = duracion_round
        self.is_rest_time = False
        
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

    def build_ui(self):
        self.clear_widgets()
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self.padding = [dp(15), dp(20)]

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

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
            text="PLAY",
            on_press=lambda x: self.start_timer(),
            background_color=(0.1, 0.4, 0.7, 1),
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
        if not self.timer_running:
            self.timer_running = True
            Clock.schedule_interval(self.update_time, 1)

    def pause_timer(self):
        self.timer_running = False
        Clock.unschedule(self.update_time)

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
        self.remaining_time = self.duracion_descanso
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_str = f"{minutes:02}:{seconds:02}"
        self.rest_indicator.text = "⏸ DESCANSO"
        
        if hasattr(self, 'parent_screen'):
            self.parent_screen.save_manual_scores()

    def start_new_round(self):
        """Inicia un nuevo round después del descanso"""
        self.is_rest_time = False
        self.remaining_time = self.duracion_round
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_str = f"{minutes:02}:{seconds:02}"
        self.rest_indicator.text = ""

    def mostrar_mensaje(self, titulo, mensaje, confirm_callback=None):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        lbl_mensaje = Label(
            text=mensaje,
            color=(0.5, 0.8, 1, 1),
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
        if hasattr(self, 'parent_screen'):
            self.parent_screen.save_manual_scores()
        
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
        if hasattr(self, 'parent_screen'):
            self.parent_screen.save_manual_scores()
        
        self.pause_timer()
        self.time_str = "FIN"
        self.time_label.text = self.time_str
        self.round_label.text = "Combate Finalizado"
        self.rest_indicator.text = ""
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
        self.ws_keepalive = None  # ⭐ Timer para mantener vivo el WebSocket
        
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)
    
    def set_competitors(self, name1, nat1, name2, nat2, combate_data=None):
        """⭐ Configura los competidores y datos del combate"""
        print("\n" + "=" * 60)
        print("[MainScreentabc] 🥋 CONFIGURANDO COMPETIDORES")
        print(f"  🔴 Rojo: {name1} ({nat1})")
        print(f"  🔵 Azul: {name2} ({nat2})")
        
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
        
        # ⭐ Conectar al WebSocket para actualizaciones en tiempo real
        if self.combate_id and WEBSOCKET_AVAILABLE:
            self.connect_websocket()
        elif not WEBSOCKET_AVAILABLE:
            print("⚠️  WebSocket no disponible - instala websocket-client")
    
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
        
        # Panel Competidor Rojo
        self.com1_panel = CompetitorPanel(
            name=name1,
            color="#E53935",
            nationality=nat1,
            alumno_id=self.id_alumno_rojo
        )
        main_layout.add_widget(self.com1_panel)

        # Panel Central
        self.center_panel = CenterPanel(
            duracion_round=duracion_round,
            duracion_descanso=duracion_descanso,
            numero_rounds=numero_rounds
        )
        self.center_panel.parent_screen = self
        main_layout.add_widget(self.center_panel)

        # Panel Competidor Azul
        self.com2_panel = CompetitorPanel(
            name=name2,
            color="#1E88E5",
            nationality=nat2,
            alumno_id=self.id_alumno_azul
        )
        main_layout.add_widget(self.com2_panel)

        self.add_widget(main_layout)
    
    def connect_websocket(self):
        """⭐ Conecta al WebSocket del tablero para recibir actualizaciones en tiempo real"""
        if not WEBSOCKET_AVAILABLE:
            print("[MainScreentabc] ✗ WebSocket no disponible")
            return
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                print(f"[WebSocket] 📨 Mensaje recibido: {data}")
                
                if data.get('event') == 'score_update':
                    # ⭐ Actualización de puntaje en tiempo real
                    alumno_id = data.get('alumnoId')
                    new_count = data.get('count', 0)
                    
                    # Actualizar el panel correspondiente
                    if alumno_id == self.id_alumno_rojo:
                        print(f"[WebSocket] 🔴 Actualizando ROJO: {new_count}")
                        self.com1_panel.update_api_score(new_count)
                    elif alumno_id == self.id_alumno_azul:
                        print(f"[WebSocket] 🔵 Actualizando AZUL: {new_count}")
                        self.com2_panel.update_api_score(new_count)
                
                elif data.get('status') == 'connected':
                    print(f"[WebSocket] ✓ Conectado al combate {data.get('combateId')}")
                    # Obtener puntajes iniciales
                    self.fetch_initial_scores()
                    
            except Exception as e:
                print(f"[WebSocket] ✗ Error procesando mensaje: {e}")
        
        def on_error(ws, error):
            print(f"[WebSocket] ✗ Error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print(f"[WebSocket] ✗ Conexión cerrada: {close_status_code} - {close_msg}")
            # ⭐ Intentar reconectar después de 3 segundos
            if self.ws_keepalive:
                Clock.schedule_once(lambda dt: self.reconnect_websocket(), 3)
        
        def on_open(ws):
            print(f"[WebSocket] ✓ Conexión establecida al combate {self.combate_id}")
            # ⭐ Iniciar keepalive para evitar timeout
            self.start_keepalive()
        
        # URL del WebSocket
        ws_url = f"ws://localhost:8080/ws/tablero/{self.combate_id}"
        print(f"\n[MainScreentabc] 🔌 Conectando a WebSocket: {ws_url}")
        
        # Crear y ejecutar WebSocket en thread separado
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        self.ws_thread = Thread(target=self.ws.run_forever, daemon=True)
        self.ws_thread.start()
    
    def start_keepalive(self):
        """⭐ Envía ping cada 30 segundos para mantener vivo el WebSocket"""
        def send_ping(dt):
            if self.ws and self.ws.sock and self.ws.sock.connected:
                try:
                    self.ws.send('ping')
                    print("[WebSocket] 💓 Keepalive ping enviado")
                except Exception as e:
                    print(f"[WebSocket] ✗ Error en keepalive: {e}")
        
        # Cancelar keepalive anterior si existe
        if self.ws_keepalive:
            self.ws_keepalive.cancel()
        
        # Programar ping cada 30 segundos
        self.ws_keepalive = Clock.schedule_interval(send_ping, 30)
        print("[WebSocket] ✓ Keepalive iniciado (ping cada 30s)")
    
    def reconnect_websocket(self):
        """⭐ Intenta reconectar el WebSocket"""
        if self.combate_id and WEBSOCKET_AVAILABLE:
            print("[WebSocket] 🔄 Intentando reconectar...")
            self.connect_websocket()
    
    def fetch_initial_scores(self):
        """Obtiene los puntajes iniciales al conectarse"""
        def work():
            try:
                # Obtener puntaje del competidor rojo
                if self.id_alumno_rojo:
                    url_rojo = f"http://localhost:8080/apiPuntajes/puntaje/alumno/{self.id_alumno_rojo}/count"
                    response_rojo = requests.get(url_rojo, timeout=2)
                    if response_rojo.status_code == 200:
                        count_rojo = response_rojo.json().get('count', 0)
                        self.com1_panel.update_api_score(count_rojo)
                        print(f"[MainScreentabc] 🔴 Puntaje inicial ROJO: {count_rojo}")
                
                # Obtener puntaje del competidor azul
                if self.id_alumno_azul:
                    url_azul = f"http://localhost:8080/apiPuntajes/puntaje/alumno/{self.id_alumno_azul}/count"
                    response_azul = requests.get(url_azul, timeout=2)
                    if response_azul.status_code == 200:
                        count_azul = response_azul.json().get('count', 0)
                        self.com2_panel.update_api_score(count_azul)
                        print(f"[MainScreentabc] 🔵 Puntaje inicial AZUL: {count_azul}")
                
                print("[MainScreentabc] ✓ Puntajes iniciales cargados\n")
                
            except Exception as e:
                print(f"[MainScreentabc] ✗ Error obteniendo puntajes iniciales: {e}")
        
        Thread(target=work, daemon=True).start()
    
    def disconnect_websocket(self):
        """Desconecta el WebSocket"""
        # Cancelar keepalive
        if self.ws_keepalive:
            self.ws_keepalive.cancel()
            self.ws_keepalive = None
        
        # Cerrar WebSocket
        if self.ws:
            try:
                self.ws.close()
                print("[MainScreentabc] ✓ WebSocket desconectado")
            except Exception as e:
                print(f"[MainScreentabc] ✗ Error al desconectar WebSocket: {e}")
    
    def save_manual_scores(self):
        """⭐ Guarda los puntajes manuales y actualiza UI inmediatamente"""
        if not self.combate_id:
            print("[MainScreentabc] ⚠️  No hay combate_id, no se pueden guardar puntos")
            return
        
        print("[MainScreentabc] 💾 Guardando puntos manuales...")
        
        def work():
            # Guardar puntos del competidor 1
            if self.com1_panel.manual_score > 0:
                success1 = self.com1_panel.save_manual_scores(self.combate_id)
                if success1:
                    # ⭐ Refrescar puntaje después de guardar
                    self.refresh_score(self.id_alumno_rojo, self.com1_panel)
            
            # Guardar puntos del competidor 2
            if self.com2_panel.manual_score > 0:
                success2 = self.com2_panel.save_manual_scores(self.combate_id)
                if success2:
                    # ⭐ Refrescar puntaje después de guardar
                    self.refresh_score(self.id_alumno_azul, self.com2_panel)
            
            self._show_save_success()
        
        Thread(target=work, daemon=True).start()
    
    def refresh_score(self, alumno_id, panel):
        """⭐ Refresca el puntaje de un alumno específico"""
        if not alumno_id:
            return
        
        try:
            url = f"http://localhost:8080/apiPuntajes/puntaje/alumno/{alumno_id}/count"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                new_count = response.json().get('count', 0)
                panel.update_api_score(new_count)
                print(f"[MainScreentabc] ✅ Puntaje actualizado para alumno {alumno_id}: {new_count}")
        except Exception as e:
            print(f"[MainScreentabc] ✗ Error refrescando puntaje: {e}")
    
    @mainthread
    def _show_save_success(self):
        print("[MainScreentabc] ✓ Puntos guardados exitosamente")
    
    @mainthread
    def _show_save_error(self):
        print("[MainScreentabc] ✗ Error al guardar algunos puntos")
    
    def reset_competitor_scores(self):
        """Reinicia los contadores de puntos manuales"""
        self.com1_panel.reset_scores()
        self.com2_panel.reset_scores()
        
    def build_ui(self):
        """Construye la UI inicial (sin datos)"""
        self.clear_widgets()
        
        orientation = ResponsiveHelper.get_layout_orientation()
        main_layout = BoxLayout(orientation=orientation, spacing=0)
        
        self.com1_panel = CompetitorPanel(
            name="COMPETIDOR 1",
            color="#E53935",
            nationality=""
        )
        main_layout.add_widget(self.com1_panel)

        self.center_panel = CenterPanel()
        self.center_panel.parent_screen = self
        main_layout.add_widget(self.center_panel)

        self.com2_panel = CompetitorPanel(
            name="COMPETIDOR 2",
            color="#1E88E5",
            nationality=""
        )
        main_layout.add_widget(self.com2_panel)

        self.add_widget(main_layout)

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)
    
    def on_pre_leave(self, *args):
        """Se ejecuta cuando se sale de esta pantalla"""
        print("[MainScreentabc] 👋 Saliendo del tablero, desconectando WebSocket...")
        self.disconnect_websocket()
        return super().on_pre_leave(*args)

# ------------------ APP DE PRUEBA ------------------
if __name__ == '__main__':
    class TestApp(App):
        def build(self):
            sm = ScreenManager()
            
            # Crear pantalla de tablero
            tablero = MainScreentabc(name='tablero_central')
            sm.add_widget(tablero)
            
            # Simular datos del combate después de 2 segundos
            def simulate_combat_creation(dt):
                print("\n" + "=" * 60)
                print("🧪 SIMULACIÓN DE COMBATE")
                print("=" * 60)
                
                combate_data = {
                    'idCombate': 1,
                    'id': 1,
                    'idAlumnoRojo': 1,
                    'idAlumnoAzul': 2,
                    'duracionRound': '00:01:00',  # 1 minuto para testing
                    'duracionDescanso': '00:00:30',  # 30 segundos para testing
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
                print("📡 Los puntajes se actualizarán en tiempo real")
                print("🎮 Conecta los ESP32 para ver actualizaciones automáticas")
                print("=" * 60 + "\n")
            
            Clock.schedule_once(simulate_combat_creation, 2)
            
            return sm
    
    TestApp().run()