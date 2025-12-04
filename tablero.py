from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.clock import Clock
from threading import Thread
from threading import Thread
from kivy.clock import Clock

# Importar cliente API si está disponible
try:
    from api_client import api
    API_AVAILABLE = True
except ImportError:
    api = None
    API_AVAILABLE = False
    print("[Tablero] Warning: api_client not found, using local scores only")


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
        """Retorna tamaño de fuente responsive"""
        width = Window.width
        height = Window.height
        if width < 600 or height < 400:
            return sp(base_size * 0.5)
        elif width < 900 or height < 600:
            return sp(base_size * 0.7)
        elif width < 1200:
            return sp(base_size * 0.85)
        return sp(base_size)
    
    @staticmethod
    def get_layout_orientation():
        """Determina si el layout debe ser vertical u horizontal"""
        width = Window.width
        height = Window.height
        if height > width or width < 800:
            return 'vertical'
        return 'horizontal'
    
    @staticmethod
    def get_spacing():
        """Retorna espaciado responsive"""
        width = Window.width
        if width < 600:
            return dp(5)
        elif width < 900:
            return dp(10)
        return dp(15)
    
    @staticmethod
    def get_padding():
        """Retorna padding responsive"""
        width = Window.width
        if width < 600:
            return dp(5)
        elif width < 900:
            return dp(8)
        return dp(10)


# ------------------ PANEL DE COMPETIDOR CON PUNTAJE ------------------
class CompetitorPanel(BoxLayout):
    score = NumericProperty(0)
    penalty_score = NumericProperty(0)
    name = StringProperty("COMPETIDOR")
    nationality = StringProperty("")
    alumno_id = NumericProperty(0)  # ID del alumno para consultar puntaje
    
    # Colores para ROJO y AZUL
    AZUL = (0.117, 0.533, 0.898, 1)
    ROJO = (0.898, 0.2, 0.2, 1)

    def __init__(self, name="COMPETIDOR", color=None, nationality="", is_red=False, alumno_id=0, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.name = name
        self.bg_color = color if color else (self.ROJO if is_red else self.AZUL)
        self.nationality = nationality
        self.is_red = is_red
        self.alumno_id = alumno_id
        self.score_refresh_event = None
        
        self.update_layout()
        Window.bind(on_resize=self.on_window_resize)
        
        self.bind(score=self.update_score_label)
        self.bind(penalty_score=self.update_penalty_label)
        self.bind(name=self.update_name_label)
        self.bind(nationality=self.update_nationality_label)

    def update_layout(self):
        self.clear_widgets()
        self.canvas.before.clear()  # Limpiar el canvas antes de dibujar
        self.spacing = ResponsiveHelper.get_spacing()
        self.padding = ResponsiveHelper.get_padding()

        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

        # Espaciador superior
        self.add_widget(BoxLayout(size_hint_y=0.05))

        # Indicador de color (ROJO/AZUL)
        color_indicator = Label(
            text="ROJO" if self.is_red else "AZUL",
            font_size=ResponsiveHelper.get_font_size(16),
            bold=True,
            color=(1, 1, 1, 0.8),
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(color_indicator)

        # Nacionalidad
        self.nationality_label = Label(
            text=self.nationality.upper() if self.nationality else "---",
            font_size=ResponsiveHelper.get_font_size(22),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(35)
        )
        self.add_widget(self.nationality_label)

        # Nombre del competidor
        self.name_label = Label(
            text=self.name,
            font_size=ResponsiveHelper.get_font_size(28),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50),
            text_size=(Window.width * 0.3, None),
            halign='center',
            valign='middle',
            shorten=True,
            shorten_from='right'
        )
        self.add_widget(self.name_label)

        # Espaciador
        self.add_widget(BoxLayout(size_hint_y=0.05))

        # Etiqueta "PUNTAJE"
        puntaje_label = Label(
            text="PUNTAJE",
            font_size=ResponsiveHelper.get_font_size(18),
            color=(1, 1, 1, 0.9),
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(puntaje_label)

        # Contenedor del puntaje con fondo
        score_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, None),
            height=dp(100),
            pos_hint={'center_x': 0.5}
        )

        with score_container.canvas.before:
            Color(1, 1, 1, 0.2)
            score_container.bg_rect = RoundedRectangle(
                pos=score_container.pos,
                size=score_container.size,
                radius=[dp(15)]
            )
        
        def update_score_bg(instance, value):
            score_container.bg_rect.pos = instance.pos
            score_container.bg_rect.size = instance.size
        
        score_container.bind(pos=update_score_bg, size=update_score_bg)

        # Label del puntaje
        self.score_label = Label(
            text=str(self.score),
            font_size=ResponsiveHelper.get_font_size(70),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=1
        )
        score_container.add_widget(self.score_label)

        self.add_widget(score_container)

        # Espaciador
        self.add_widget(BoxLayout(size_hint_y=0.05))

        # Sección de penalizaciones (Gam-jeom)
        penalty_label = Label(
            text="FALTAS",
            font_size=ResponsiveHelper.get_font_size(16),
            color=(1, 1, 1, 0.8),
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(penalty_label)

        # Número de penalizaciones (simple)
        self.penalty_count_label = Label(
            text=str(self.penalty_score),
            font_size=ResponsiveHelper.get_font_size(40),
            color=(1, 1, 0, 1),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.add_widget(self.penalty_count_label)

        # Espaciador inferior
        self.add_widget(BoxLayout(size_hint_y=0.1))

    def update_score_label(self, instance, value):
        if hasattr(self, 'score_label'):
            self.score_label.text = str(value)

    def update_penalty_label(self, instance, value):
        if hasattr(self, 'penalty_count_label'):
            self.penalty_count_label.text = str(value)

    def update_name_label(self, instance, value):
        if hasattr(self, 'name_label'):
            self.name_label.text = value

    def update_nationality_label(self, instance, value):
        if hasattr(self, 'nationality_label'):
            self.nationality_label.text = value.upper() if value else "---"

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.update_layout(), 0.1)

    def add_score(self, points=1):
        """Añade puntos al marcador"""
        self.score += points

    def subtract_score(self, points=1):
        """Resta puntos del marcador"""
        if self.score >= points:
            self.score -= points

    def add_penalty(self):
        """Añade una penalización"""
        if self.penalty_score < 10:
            self.penalty_score += 1

    def reset(self):
        """Reinicia el panel"""
        self.score = 0
        self.penalty_score = 0
        self.stop_score_refresh()

    def load_score_from_api(self):
        """Carga el puntaje desde la API"""
        if not API_AVAILABLE or not api or self.alumno_id <= 0:
            return
        
        def _fetch_score():
            try:
                count = api.get_puntaje_count(self.alumno_id)
                Clock.schedule_once(lambda dt: self._update_score_from_api(count))
            except Exception as e:
                print(f"[CompetitorPanel] Error al obtener puntaje: {e}")
        
        thread = Thread(target=_fetch_score)
        thread.daemon = True
        thread.start()

    def load_gamjeom_from_api(self, combate_id):
        """Carga las faltas GAM-JEOM desde la API"""
        if not API_AVAILABLE or not api or self.alumno_id <= 0 or not combate_id:
            return
        
        def _fetch_gamjeom():
            try:
                import requests
                url = f"http://localhost:8080/apiGamJeom/falta/alumno/{self.alumno_id}/combate/{combate_id}/count"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    count = data.get('count', 0)
                    Clock.schedule_once(lambda dt: self._update_gamjeom_from_api(count))
            except Exception as e:
                print(f"[CompetitorPanel] Error al obtener GAM-JEOM: {e}")
    
        thread = Thread(target=_fetch_gamjeom)
        thread.daemon = True
        thread.start()

    def _update_gamjeom_from_api(self, count):
        """Actualiza las faltas GAM-JEOM en el hilo principal"""
        if count is not None:
            self.penalty_score = count

    def _update_score_from_api(self, count):
        """Actualiza el puntaje en el hilo principal"""
        if count is not None:
            self.score = count

    def start_score_refresh(self, combate_id=None, interval=2.0):
        """Inicia la actualización periódica del puntaje y GAM-JEOM"""
        self.stop_score_refresh()
        self.combate_id_for_refresh = combate_id
        
        if self.alumno_id > 0:
            self.load_score_from_api()  # Cargar puntaje inmediatamente
            if combate_id:
                self.load_gamjeom_from_api(combate_id)  # Cargar GAM-JEOM inmediatamente
            
            self.score_refresh_event = Clock.schedule_interval(
                lambda dt: self._refresh_all_data(), 
                interval
            )

    def _refresh_all_data(self):
        """Refresca tanto puntajes como GAM-JEOM"""
        self.load_score_from_api()
        if hasattr(self, 'combate_id_for_refresh') and self.combate_id_for_refresh:
            self.load_gamjeom_from_api(self.combate_id_for_refresh)
    
    def stop_score_refresh(self):
        """Detiene la actualización periódica del puntaje"""
        if self.score_refresh_event:
            self.score_refresh_event.cancel()
            self.score_refresh_event = None


# ------------------ PANEL CENTRAL RESPONSIVE ------------------
class CenterPanel(BoxLayout):
    time_str = StringProperty("00:00")
    round_num = NumericProperty(1)
    total_rounds = NumericProperty(3)
    match_status = StringProperty("LISTO")
    categoria = StringProperty("")
    area = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Timer variables
        self.time_seconds = 0
        self.round_duration = 120  # 2 minutos por defecto
        self.rest_duration = 60    # 1 minuto de descanso
        self.is_running = False
        self.is_rest = False
        self.timer_event = None
        
        self.update_layout()
        Window.bind(on_resize=self.on_window_resize)

    def update_layout(self):
        self.clear_widgets()
        self.canvas.before.clear()  # Limpiar el canvas antes de dibujar
        self.spacing = ResponsiveHelper.get_spacing()
        self.padding = ResponsiveHelper.get_padding()

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Espaciador superior
        self.add_widget(BoxLayout(size_hint_y=0.05))

        # Información del combate (categoría/área)
        if self.categoria or self.area:
            info_text = self.categoria if self.categoria else self.area
            info_label = Label(
                text=info_text.upper(),
                font_size=ResponsiveHelper.get_font_size(16),
                color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(25)
            )
            self.add_widget(info_label)

        # Estado del combate
        self.status_label = Label(
            text=self.match_status,
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.1, 0.6, 0.1, 1) if self.match_status == "EN CURSO" else (0.5, 0.5, 0.5, 1),
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(self.status_label)

        # Espaciador
        self.add_widget(BoxLayout(size_hint_y=0.05))

        # Etiqueta "RONDA"
        ronda_label = Label(
            text="RONDAS",
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(ronda_label)

        # Número de ronda con total
        self.round_label = Label(
            text=f"{self.total_rounds}",
            font_size=ResponsiveHelper.get_font_size(45),
            color=(0.1, 0.4, 0.7, 1),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        self.add_widget(self.round_label)

        # Espaciador
        self.add_widget(BoxLayout(size_hint_y=0.05))

        # Contenedor del tiempo con fondo
        time_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.9, None),
            height=dp(120),
            pos_hint={'center_x': 0.5}
        )

        with time_container.canvas.before:
            Color(0.1, 0.4, 0.7, 0.1)
            time_container.bg_rect = RoundedRectangle(
                pos=time_container.pos,
                size=time_container.size,
                radius=[dp(15)]
            )
        
        def update_time_bg(instance, value):
            time_container.bg_rect.pos = instance.pos
            time_container.bg_rect.size = instance.size
        
        time_container.bind(pos=update_time_bg, size=update_time_bg)

        # Etiqueta "TIEMPO"
        tiempo_label = Label(
            text="DESCANSO" if self.is_rest else "TIEMPO",
            font_size=ResponsiveHelper.get_font_size(16),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=0.25
        )
        time_container.add_widget(tiempo_label)

        # Tiempo
        self.time_label = Label(
            text=self.time_str,
            font_size=ResponsiveHelper.get_font_size(55),
            color=(0.1, 0.1, 0.1, 1),
            bold=True,
            size_hint_y=0.75
        )
        time_container.add_widget(self.time_label)

        self.add_widget(time_container)

        # Espaciador
        self.add_widget(BoxLayout(size_hint_y=0.1))

        # Botón VOLVER
        back_button_container = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=[dp(10), 0, dp(10), dp(10)]
        )
        
        self.back_button = Button(
            text="VOLVER",
            size_hint=(1, 1),
            background_normal='',
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(16)
        )
        
        with self.back_button.canvas.before:
            Color(0.5, 0.5, 0.5, 1)
            self.back_button.rect = RoundedRectangle(
                pos=self.back_button.pos,
                size=self.back_button.size,
                radius=[dp(12)]
            )
        
        def update_button_rect(instance, value):
            self.back_button.rect.pos = instance.pos
            self.back_button.rect.size = instance.size
        
        self.back_button.bind(pos=update_button_rect, size=update_button_rect)
        self.back_button.bind(on_press=self.go_back)
        
        back_button_container.add_widget(self.back_button)
        self.add_widget(back_button_container)

        # Espaciador inferior
        self.add_widget(BoxLayout(size_hint_y=0.02))

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def toggle_timer(self, instance):
        """Inicia o pausa el timer"""
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        """Inicia el timer"""
        self.is_running = True
        self.match_status = "EN CURSO"
        
        if self.timer_event:
            self.timer_event.cancel()
        
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        self.update_status_label()

    def pause_timer(self):
        """Pausa el timer"""
        self.is_running = False
        self.match_status = "PAUSADO"
        
        if self.timer_event:
            self.timer_event.cancel()
        
        self.update_status_label()

    def reset_timer(self, instance=None):
        """Reinicia el timer del round actual"""
        self.time_seconds = self.round_duration if not self.is_rest else self.rest_duration
        self.update_time_display()
        
        if self.is_running:
            self.pause_timer()

    def update_timer(self, dt):
        """Actualiza el timer cada segundo"""
        if self.time_seconds > 0:
            self.time_seconds -= 1
            self.update_time_display()
        else:
            # Tiempo agotado
            if self.is_rest:
                # Fin del descanso, siguiente round
                self.is_rest = False
                self.round_num += 1
                if self.round_num > self.total_rounds:
                    self.end_match()
                else:
                    self.time_seconds = self.round_duration
                    self.update_layout()
            else:
                # Fin del round
                if self.round_num < self.total_rounds:
                    self.is_rest = True
                    self.time_seconds = self.rest_duration
                    self.update_layout()
                else:
                    self.end_match()

    def end_match(self):
        """Finaliza el combate"""
        self.pause_timer()
        self.match_status = "FINALIZADO"
        self.update_status_label()

    def update_time_display(self):
        """Actualiza la visualización del tiempo"""
        minutes = self.time_seconds // 60
        seconds = self.time_seconds % 60
        self.time_str = f"{minutes:02d}:{seconds:02d}"
        if hasattr(self, 'time_label'):
            self.time_label.text = self.time_str

    def update_status_label(self):
        """Actualiza el label de estado"""
        if hasattr(self, 'status_label'):
            self.status_label.text = self.match_status
            if self.match_status == "EN CURSO":
                self.status_label.color = (0.1, 0.6, 0.1, 1)
            elif self.match_status == "PAUSADO":
                self.status_label.color = (0.9, 0.6, 0.1, 1)
            elif self.match_status == "FINALIZADO":
                self.status_label.color = (0.8, 0.1, 0.1, 1)
            else:
                self.status_label.color = (0.5, 0.5, 0.5, 1)

    def go_back(self, instance):
        """Vuelve a la pantalla anterior"""
        # Pausar timer si está corriendo
        if self.is_running:
            self.pause_timer()
        
        app = App.get_running_app()
        if app.root.has_screen('combates_anteriores'):
            app.root.current = 'combates_anteriores'
        else:
            app.root.current = 'ini'
    
    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.update_layout(), 0.1)

    def set_round_config(self, num_rounds, round_duration, rest_duration):
        """Configura los parámetros de rounds"""
        self.total_rounds = num_rounds
        self.round_duration = round_duration
        self.rest_duration = rest_duration
        self.time_seconds = round_duration
        self.update_time_display()
        self.update_layout()


# ------------------ PANTALLA PRINCIPAL DEL TABLERO ------------------
class MainScreentab(Screen):
    combate_data = ObjectProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.combate_data = None
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

    def build_ui(self):
        self.clear_widgets()
        
        orientation = ResponsiveHelper.get_layout_orientation()
        
        main_layout = BoxLayout(
            orientation=orientation,
            spacing=0
        )

        # Panel Competidor 1 (AZUL - izquierda)
        self.com1_panel = CompetitorPanel(
            name="COMPETIDOR 1",
            is_red=False,
            nationality=""
        )
        main_layout.add_widget(self.com1_panel)

        # Panel Central
        self.center_panel = CenterPanel()
        main_layout.add_widget(self.center_panel)

        # Panel Competidor 2 (ROJO - derecha)
        self.com2_panel = CompetitorPanel(
            name="COMPETIDOR 2",
            is_red=True,
            nationality=""
        )
        main_layout.add_widget(self.com2_panel)

        self.add_widget(main_layout)

    def on_enter(self):
        """Se ejecuta cuando se entra a la pantalla"""
        # Si hay datos del combate, aplicarlos
        if self.combate_data:
            self.load_combate_data(self.combate_data)

    def load_combate_data(self, data):
        """Carga los datos del combate en el tablero"""
        if not data:
            return
        
        print(f"[Tablero] Cargando datos del combate: {data}")
        
        # Detener actualizaciones previas
        self.com1_panel.stop_score_refresh()
        self.com2_panel.stop_score_refresh()
        
        # Competidor 1 (Azul)
        self.com1_panel.name = data.get('competidor1', 'COMPETIDOR 1')
        self.com1_panel.nationality = data.get('nacionalidad1', '')
        self.com1_panel.alumno_id = data.get('alumno_id_azul', 0) or data.get('id_alumno1', 0)
        
        # Competidor 2 (Rojo)
        self.com2_panel.name = data.get('competidor2', 'COMPETIDOR 2')
        self.com2_panel.nationality = data.get('nacionalidad2', '')
        self.com2_panel.alumno_id = data.get('alumno_id_rojo', 0) or data.get('id_alumno2', 0)
        
        # Reiniciar puntajes locales
        self.com1_panel.score = 0
        self.com1_panel.penalty_score = 0
        self.com2_panel.score = 0
        self.com2_panel.penalty_score = 0
        
        # Configuración del combate
        self.center_panel.categoria = data.get('categoria', '')
        self.center_panel.area = data.get('area', '')
        
        # Configuración de rounds
        num_rounds = data.get('num_rounds', 3)
        duracion_round = data.get('duracion_round', 120)  # en segundos
        duracion_descanso = data.get('duracion_descanso', 60)  # en segundos
        
        self.center_panel.set_round_config(num_rounds, duracion_round, duracion_descanso)
        self.center_panel.round_num = 1
        self.center_panel.match_status = "LISTO"
        
        # Reconstruir la UI para reflejar los cambios
        self.com1_panel.update_layout()
        self.com2_panel.update_layout()
        self.center_panel.update_layout()

        # Obtener ID del combate
        combate_id = data.get('idCombate') or data.get('id') or data.get('combate_id')

        # Cargar puntajes y GAM-JEOM UNA SOLA VEZ
        self.com1_panel.load_score_from_api()
        self.com2_panel.load_score_from_api()

        if combate_id:
            self.com1_panel.load_gamjeom_from_api(combate_id)
            self.com2_panel.load_gamjeom_from_api(combate_id)
        else:
            print("[Tablero] ⚠️ No se proporcionó ID de combate, no se cargarán GAM-JEOM")

        # NO llamar a start_score_refresh() - así no hay polling

    def set_combate_data(self, data):
        """Establece los datos del combate"""
        self.combate_data = data
        self.load_combate_data(data)
    
    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)
        # Recargar datos después de reconstruir UI
        if self.combate_data:
            Clock.schedule_once(lambda dt: self.load_combate_data(self.combate_data), 0.2)


# ------------------ APLICACIÓN STANDALONE ------------------
class TableroApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Pantalla del tablero
        tablero = MainScreentab(name='tablero')
        sm.add_widget(tablero)
        
        # Datos de prueba
        test_data = {
            'competidor1': 'Juan Pérez',
            'competidor2': 'Carlos García',
            'nacionalidad1': 'MEX',
            'nacionalidad2': 'USA',
            'peso1': 68,
            'peso2': 70,
            'categoria': 'Welter',
            'area': 'Área A',
            'num_rounds': 3,
            'duracion_round': 120,
            'duracion_descanso': 60
        }
        
        # Cargar datos de prueba
        Clock.schedule_once(lambda dt: tablero.load_combate_data(test_data), 0.5)
        
        return sm


if __name__ == '__main__':
    TableroApp().run()