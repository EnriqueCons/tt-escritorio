from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.app import App
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty
from datetime import datetime, date
import calendar
from threading import Thread

# Importar el cliente API
try:
    from api_client import api
except ImportError:
    api = None
    print("[ActualizarCombateScreen] Warning: api_client not found")


class DateSelector(BoxLayout):
    selected_date = ObjectProperty(date.today())
    
    def __init__(self, initial_date=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(55)
        
        # Parsear fecha inicial
        parsed_date = date.today()
        if initial_date:
            try:
                if isinstance(initial_date, str):
                    if '/' in initial_date:
                        day, month, year = map(int, initial_date.split('/'))
                        parsed_date = date(year, month, day)
                    elif '-' in initial_date:
                        year, month, day = map(int, initial_date.split('-'))
                        parsed_date = date(year, month, day)
                elif isinstance(initial_date, date):
                    parsed_date = initial_date
            except Exception as e:
                print(f"[DateSelector] Error parsing date: {e}")
                parsed_date = date.today()
        
        current_year = parsed_date.year
        self.year_spinner = Spinner(
            text=str(current_year),
            values=[str(y) for y in range(current_year - 100, current_year + 10)],
            size_hint=(0.3, 1),
            font_size=sp(20),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1)
        )
        
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        self.month_spinner = Spinner(
            text=meses[parsed_date.month - 1],
            values=meses,
            size_hint=(0.4, 1),
            font_size=sp(20),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1))
        
        self.day_spinner = Spinner(
            text=str(parsed_date.day),
            values=[],
            size_hint=(0.3, 1),
            font_size=sp(20),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1))
        
        self.add_widget(self.day_spinner)
        self.add_widget(self.month_spinner)
        self.add_widget(self.year_spinner)
        
        self.update_days()
        self.month_spinner.bind(text=self.update_days_on_change)
        self.year_spinner.bind(text=self.update_days_on_change)
        
    def update_days_on_change(self, *args):
        self.update_days()
        self.get_selected_date()
        
    def update_days(self):
        month = self.month_spinner.text
        year = self.year_spinner.text
        
        if month and year:
            meses_e = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            month_num = meses_e.index(month) + 1
            year_num = int(year)
            _, num_days = calendar.monthrange(year_num, month_num)
            
            current_day = int(self.day_spinner.text) if self.day_spinner.text.isdigit() else 1
            days = [str(d) for d in range(1, num_days + 1)]
            self.day_spinner.values = days
            
            if str(current_day) not in days:
                current_day = 1
            self.day_spinner.text = str(current_day)
            
    def get_selected_date(self):
        try:
            meses_espanol = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            month_num = meses_espanol.index(self.month_spinner.text) + 1
            day = int(self.day_spinner.text)
            year = int(self.year_spinner.text)
            self.selected_date = date(year, month_num, day)
            return self.selected_date
        except:
            return date.today()
            
    def get_formatted_date(self):
        selected_date = self.get_selected_date()
        return selected_date.strftime("%d/%m/%Y")
    
    def set_date(self, date_str):
        """Establece la fecha desde un string dd/mm/yyyy o yyyy-mm-dd"""
        try:
            if isinstance(date_str, str):
                if '/' in date_str:
                    day, month, year = map(int, date_str.split('/'))
                elif '-' in date_str:
                    year, month, day = map(int, date_str.split('-'))
                else:
                    return
                    
                meses = [
                    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                ]
                
                self.year_spinner.text = str(year)
                self.month_spinner.text = meses[month - 1]
                self.update_days()
                self.day_spinner.text = str(day)
        except Exception as e:
            print(f"[DateSelector] Error setting date: {e}")


class TimeSelector(BoxLayout):
    selected_time = ObjectProperty(None)
    
    def __init__(self, initial_time=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(55)
        
        # Parsear hora inicial
        parsed_time = datetime.now().time()
        if initial_time:
            try:
                if isinstance(initial_time, str) and ':' in initial_time:
                    parts = initial_time.split(':')
                    hour = int(parts[0])
                    minute = int(parts[1]) if len(parts) > 1 else 0
                    parsed_time = datetime.now().replace(hour=hour, minute=minute).time()
            except Exception as e:
                print(f"[TimeSelector] Error parsing time: {e}")
        
        self.hour_spinner = Spinner(
            text=f"{parsed_time.hour:02d}",
            values=[f"{h:02d}" for h in range(0, 24)],
            size_hint=(0.45, 1),
            font_size=sp(20),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1))
        
        minute = (parsed_time.minute // 5) * 5 
        self.minute_spinner = Spinner(
            text=f"{minute:02d}",
            values=[f"{m:02d}" for m in range(0, 60, 5)],
            size_hint=(0.45, 1),
            font_size=sp(20),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1))
        
        self.add_widget(self.hour_spinner)
        self.add_widget(Label(text=":", size_hint=(0.1, 1)))
        self.add_widget(self.minute_spinner)
        
        self.get_selected_time()
        self.hour_spinner.bind(text=self.update_time)
        self.minute_spinner.bind(text=self.update_time)
        
    def update_time(self, *args):
        self.get_selected_time()
        
    def get_selected_time(self):
        try:
            hour = int(self.hour_spinner.text)
            minute = int(self.minute_spinner.text)
            self.selected_time = datetime.now().replace(hour=hour, minute=minute).time()
            return self.selected_time
        except:
            return datetime.now().time()
            
    def get_formatted_time(self):
        selected_time = self.get_selected_time()
        return selected_time.strftime("%H:%M")
    
    def set_time(self, time_str):
        """Establece la hora desde un string HH:MM o HH:MM:SS"""
        try:
            if isinstance(time_str, str) and ':' in time_str:
                parts = time_str.split(':')
                self.hour_spinner.text = f"{int(parts[0]):02d}"
                minute = int(parts[1]) if len(parts) > 1 else 0
                minute = (minute // 5) * 5
                self.minute_spinner.text = f"{minute:02d}"
        except Exception as e:
            print(f"[TimeSelector] Error setting time: {e}")


class RoundsSelector(BoxLayout):
    selected_rounds = ObjectProperty(3)
    
    def __init__(self, initial_rounds=3, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(5)
        self.size_hint = (1, None) 
        self.height = dp(55)
       
        self.rounds_spinner = Spinner(
            text=str(initial_rounds),
            values=[str(r) for r in range(1, 6)],
            size_hint=(1, 1), 
            font_size=sp(20),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1)
        )
        
        self.add_widget(self.rounds_spinner)
        self.get_selected_rounds()
        self.rounds_spinner.bind(text=self.update_rounds)
        
    def update_rounds(self, *args):
        self.get_selected_rounds()
        
    def get_selected_rounds(self):
        try:
            self.selected_rounds = int(self.rounds_spinner.text)
            return self.selected_rounds
        except:
            return 3
    
    def set_rounds(self, num_rounds):
        """Establece el número de rounds"""
        try:
            num = int(num_rounds)
            if 1 <= num <= 5:
                self.rounds_spinner.text = str(num)
        except:
            pass


class DurationSelector(BoxLayout):
    selected_minutes = ObjectProperty(0)
    selected_seconds = ObjectProperty(0)
    
    def __init__(self, initial_minutes=3, initial_seconds=0, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(55)  
        
        self.minutes_spinner = Spinner(
            text=str(initial_minutes),
            values=[str(m) for m in range(0, 11)],
            size_hint=(0.3, 1),  
            font_size=sp(20),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1)
        )
        
        self.seconds_spinner = Spinner(
            text=f"{initial_seconds:02d}",
            values=[f"{s:02d}" for s in range(0, 60, 5)],
            size_hint=(0.3, 1),  
            font_size=sp(20),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1)
        )
        
        self.add_widget(self.minutes_spinner)
        self.add_widget(Label(text="min", size_hint=(0.15, 1), font_size=sp(16)))
        self.add_widget(Label(text=":", size_hint=(0.1, 1), font_size=sp(20)))
        self.add_widget(self.seconds_spinner)
        self.add_widget(Label(text="seg", size_hint=(0.15, 1), font_size=sp(16)))
        
        self.get_selected_duration()
        self.minutes_spinner.bind(text=self.update_duration)
        self.seconds_spinner.bind(text=self.update_duration)
        
    def update_duration(self, *args):
        self.get_selected_duration()
        
    def get_selected_duration(self):
        try:
            self.selected_minutes = int(self.minutes_spinner.text)
            self.selected_seconds = int(self.seconds_spinner.text)
            return self.selected_minutes * 60 + self.selected_seconds
        except:
            return 0
            
    def get_formatted_duration(self):
        return f"{self.selected_minutes}:{self.selected_seconds:02d}"
    
    def get_api_format(self):
        """Retorna en formato HH:mm:ss para la API"""
        total_seconds = self.get_selected_duration()
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def set_duration_from_seconds(self, total_seconds):
        """Establece la duración desde segundos totales"""
        try:
            total_seconds = int(total_seconds)
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            seconds = (seconds // 5) * 5
            self.minutes_spinner.text = str(min(minutes, 10))
            self.seconds_spinner.text = f"{seconds:02d}"
        except:
            pass


class CategoriaPesoSelector(BoxLayout):
    selected_category = ObjectProperty("")
    
    def __init__(self, initial_category="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(55)
        
        categorias = [
            "Fin", "Fly", "Bantam", "Feather", 
            "Light", "Welter", "Middle", "Heavy"
        ]
        
        initial = initial_category if initial_category in categorias else categorias[0]
        
        self.category_spinner = Spinner(
            text=initial,
            values=categorias,
            size_hint=(1, 1),
            font_size=sp(20),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1))
        
        self.add_widget(self.category_spinner)
        self.get_selected_category()
        self.category_spinner.bind(text=self.update_category)
        
    def update_category(self, *args):
        self.get_selected_category()
        
    def get_selected_category(self):
        self.selected_category = self.category_spinner.text
        return self.selected_category
    
    def set_category(self, category):
        """Establece la categoría"""
        categorias = [
            "Fin", "Fly", "Bantam", "Feather", 
            "Light", "Welter", "Middle", "Heavy"
        ]
        if category in categorias:
            self.category_spinner.text = category


class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_active = ""
        self.background_color = (0, 0, 0, 0)
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(55)
        self.padding = [dp(8), dp(8), dp(8), dp(8)]
        self.font_size = sp(24)
        self.color = (1, 1, 1, 1)
        self.hint_text_color = (0.9, 0.9, 0.9, 0.9)
        self.cursor_color = (1, 1, 1, 1)
        self.selection_color = (0.2, 0.6, 1, 0.5)
        self.bold = True

        with self.canvas.before:
            Color(0.1, 0.4, 0.7, 0.9)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            Color(1, 1, 1, 0.3)
            self.border_rect = RoundedRectangle(
                pos=(self.pos[0]+dp(2), self.pos[1]+dp(2)),
                size=(self.size[0]-dp(4), self.size[1]-dp(4)),
                radius=[dp(8)]
            )

        self.bind(pos=self._update_rects, size=self._update_rects)

    def _update_rects(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.pos[0]+dp(2), self.pos[1]+dp(2))
        self.border_rect.size = (self.size[0]-dp(4), self.size[1]-dp(4))

    def on_focus(self, instance, value):
        if value:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0.2, 0.5, 0.9, 1)
                self.bg_rect = RoundedRectangle(
                    pos=self.pos,
                    size=self.size,
                    radius=[dp(12)]
                )
                Color(1, 1, 1, 0.5)
                self.border_rect = RoundedRectangle(
                    pos=(self.pos[0]+dp(2), self.pos[1]+dp(2)),
                    size=(self.size[0]-dp(4), self.size[1]-dp(4)),
                    radius=[dp(8)]
                )
        else:
            self._update_rects()
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0.1, 0.4, 0.7, 0.9)
                self.bg_rect = RoundedRectangle(
                    pos=self.pos,
                    size=self.size,
                    radius=[dp(12)]
                )
                Color(1, 1, 1, 0.3)
                self.border_rect = RoundedRectangle(
                    pos=(self.pos[0]+dp(2), self.pos[1]+dp(2)),
                    size=(self.size[0]-dp(4), self.size[1]-dp(4)),
                    radius=[dp(8)]
                )


class HoverButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.1, 0.4, 0.7, 1)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = dp(20)
        self.bold = True
        self.border_radius = dp(10)

        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.border_radius])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ActualizarCombateScreen(Screen):
    combate_data = ObjectProperty(None, allownone=True)
    on_save = ObjectProperty(None, allownone=True)
    
    def __init__(self, combate_data=None, on_save=None, **kwargs):
        self.combate_data = combate_data
        self.on_save_callback = on_save
        self.is_edit_mode = combate_data is not None
        super().__init__(**kwargs)
        self.build_ui()
        
        # Precargar datos si estamos en modo edición
        if self.is_edit_mode:
            Clock.schedule_once(lambda dt: self.precargar_datos(), 0.1)

    def build_ui(self):
        self.clear_widgets()
        
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(10)],
            spacing=dp(10)
        )

        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.background_rect = Rectangle(size=Window.size, pos=self.pos)

        self.bind(size=self.update_background, pos=self.update_background)

        # Logo
        logo = Image(
            source="Imagen5-Photoroom.png",
            size_hint=(1, None),
            height=dp(120),
            pos_hint={'center_x': 0.5}
        )
        main_layout.add_widget(logo)

        # ScrollView
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=dp(10),
            scroll_type=['bars', 'content']
        )

        # Contenedor del formulario
        form_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            spacing=dp(12),
            padding=[dp(30), dp(20), dp(30), dp(20)],
            pos_hint={'center_x': 0.5}
        )
        form_container.bind(minimum_height=form_container.setter('height'))

        # Título dinámico
        titulo_text = 'EDITAR COMBATE' if self.is_edit_mode else 'CREAR COMBATE'
        if self.is_edit_mode and self.combate_data:
            titulo_text = f'EDITAR COMBATE #{self.combate_data.get("numero", "")}'
            
        titulo = Label(
            text=titulo_text,
            font_size=dp(32),
            color=(0.1, 0.4, 0.7),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        form_container.add_widget(titulo)

        # Función para crear campos
        def crear_campo(texto, hint_text=None, widget=None):
            campo_layout = BoxLayout(
                orientation='vertical',
                spacing=dp(5),
                size_hint_y=None,
                height=dp(85)
            )
            campo_layout.add_widget(Label(
                text=texto,
                font_size=dp(18),
                color=(0.1, 0.1, 0.2, 1),
                size_hint_y=None,
                height=dp(25)
            ))
            if widget:
                campo_layout.add_widget(widget)
                return campo_layout, widget
            else:
                input_field = RoundedTextInput(hint_text=hint_text)
                campo_layout.add_widget(input_field)
                return campo_layout, input_field

        # ========== SECCIÓN: COMPETIDORES ==========
        competidores_label = Label(
            text='Datos de los Competidores',
            font_size=dp(26),
            color=(0.1, 0.4, 0.7),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        form_container.add_widget(competidores_label)

        # COMPETIDOR 1 (ROJO)
        competidor1_label = Label(
            text='COMPETIDOR 1 (ROJO)',
            font_size=dp(22),
            color=(0.8, 0.2, 0.2),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        form_container.add_widget(competidor1_label)

        competidor1_layout, self.competidor1_input = crear_campo('Nombre(s)', 'Nombre(s)')
        form_container.add_widget(competidor1_layout)

        self.fecha_nac1_selector = DateSelector()
        fecha_nac1_layout, _ = crear_campo('Fecha de Nacimiento', widget=self.fecha_nac1_selector)
        form_container.add_widget(fecha_nac1_layout)

        peso1_layout, self.peso1_input = crear_campo('Peso (kg)', 'Peso')
        form_container.add_widget(peso1_layout)

        sexo1_layout, self.sexo1_input = crear_campo('Sexo', 'M / F')
        form_container.add_widget(sexo1_layout)

        nacionalidad1_layout, self.nacionalidad1_input = crear_campo('Nacionalidad', 'Nacionalidad')
        form_container.add_widget(nacionalidad1_layout)

        # Separador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(20)))

        # COMPETIDOR 2 (AZUL)
        competidor2_label = Label(
            text='COMPETIDOR 2 (AZUL)',
            font_size=dp(22),
            color=(0.2, 0.4, 0.8),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        form_container.add_widget(competidor2_label)

        competidor2_layout, self.competidor2_input = crear_campo('Nombre(s)', 'Nombre(s)')
        form_container.add_widget(competidor2_layout)

        self.fecha_nac2_selector = DateSelector()
        fecha_nac2_layout, _ = crear_campo('Fecha de Nacimiento', widget=self.fecha_nac2_selector)
        form_container.add_widget(fecha_nac2_layout)

        peso2_layout, self.peso2_input = crear_campo('Peso (kg)', 'Peso')
        form_container.add_widget(peso2_layout)

        sexo2_layout, self.sexo2_input = crear_campo('Sexo', 'M / F')
        form_container.add_widget(sexo2_layout)

        nacionalidad2_layout, self.nacionalidad2_input = crear_campo('Nacionalidad', 'Nacionalidad')
        form_container.add_widget(nacionalidad2_layout)

        # Separador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(20)))

        # ========== SECCIÓN: DATOS DEL COMBATE ==========
        combate_label = Label(
            text='Datos del Combate',
            font_size=dp(26),
            color=(0.1, 0.4, 0.7),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        form_container.add_widget(combate_label)

        self.fecha_combate_selector = DateSelector()
        fecha_combate_layout, _ = crear_campo('Fecha del Combate', widget=self.fecha_combate_selector)
        form_container.add_widget(fecha_combate_layout)

        self.hora_combate_selector = TimeSelector()
        hora_combate_layout, _ = crear_campo('Hora del Combate', widget=self.hora_combate_selector)
        form_container.add_widget(hora_combate_layout)

        area_layout, self.area_input = crear_campo('Área de Combate', 'Ej: Área A, Tatami 1')
        form_container.add_widget(area_layout)

        self.categoria_peso_selector = CategoriaPesoSelector()
        categoria_peso_layout, _ = crear_campo('Categoría', widget=self.categoria_peso_selector)
        form_container.add_widget(categoria_peso_layout)

        self.rounds_selector = RoundsSelector(initial_rounds=3)
        rounds_layout, _ = crear_campo('Número de Rounds', widget=self.rounds_selector)
        form_container.add_widget(rounds_layout)

        self.duracion_round_selector = DurationSelector(initial_minutes=3, initial_seconds=0)
        duracion_round_layout, _ = crear_campo('Duración del Round', widget=self.duracion_round_selector)
        form_container.add_widget(duracion_round_layout)

        self.duracion_descanso_selector = DurationSelector(initial_minutes=1, initial_seconds=0)
        duracion_descanso_layout, _ = crear_campo('Duración del Descanso', widget=self.duracion_descanso_selector)
        form_container.add_widget(duracion_descanso_layout)

        # Separador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(20)))

        # ========== SECCIÓN: JUECES ==========
        jueces_label = Label(
            text='Jueces',
            font_size=dp(26),
            color=(0.1, 0.4, 0.7),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        form_container.add_widget(jueces_label)

        # Juez Central
        arbitro_label = Label(
            text='JUEZ CENTRAL',
            font_size=dp(22),
            color=(0.1, 0.4, 0.7),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        form_container.add_widget(arbitro_label)

        arbitro_nombre_layout, self.arbitro_nombre_input = crear_campo('Nombre(s)', 'Nombre(s) del árbitro')
        form_container.add_widget(arbitro_nombre_layout)

        arbitro_apellidos_layout, self.arbitro_apellidos_input = crear_campo('Apellidos', 'Apellidos del árbitro')
        form_container.add_widget(arbitro_apellidos_layout)

        # Juez 1
        juez1_label = Label(text='JUEZ 1', font_size=dp(22), color=(0.1, 0.4, 0.7), bold=True, size_hint_y=None, height=dp(40))
        form_container.add_widget(juez1_label)

        juez1_nombre_layout, self.juez1_nombre_input = crear_campo('Nombre(s)', 'Nombre(s) del juez 1')
        form_container.add_widget(juez1_nombre_layout)

        juez1_apellidos_layout, self.juez1_apellidos_input = crear_campo('Apellidos', 'Apellidos del juez 1')
        form_container.add_widget(juez1_apellidos_layout)

        # Juez 2
        juez2_label = Label(text='JUEZ 2', font_size=dp(22), color=(0.1, 0.4, 0.7), bold=True, size_hint_y=None, height=dp(40))
        form_container.add_widget(juez2_label)

        juez2_nombre_layout, self.juez2_nombre_input = crear_campo('Nombre(s)', 'Nombre(s) del juez 2')
        form_container.add_widget(juez2_nombre_layout)

        juez2_apellidos_layout, self.juez2_apellidos_input = crear_campo('Apellidos', 'Apellidos del juez 2')
        form_container.add_widget(juez2_apellidos_layout)

        # Juez 3
        juez3_label = Label(text='JUEZ 3', font_size=dp(22), color=(0.1, 0.4, 0.7), bold=True, size_hint_y=None, height=dp(40))
        form_container.add_widget(juez3_label)

        juez3_nombre_layout, self.juez3_nombre_input = crear_campo('Nombre(s)', 'Nombre(s) del juez 3')
        form_container.add_widget(juez3_nombre_layout)

        juez3_apellidos_layout, self.juez3_apellidos_input = crear_campo('Apellidos', 'Apellidos del juez 3')
        form_container.add_widget(juez3_apellidos_layout)

        # ========== BOTONES ==========
        botones_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(50),
            padding=[0, dp(20), 0, 0]
        )

        # Botón principal dinámico
        btn_text = 'GUARDAR CAMBIOS' if self.is_edit_mode else 'CREAR COMBATE'
        btn_accion = HoverButton(text=btn_text)
        btn_accion.bind(on_press=self.guardar_combate)
        botones_layout.add_widget(btn_accion)

        btn_volver = HoverButton(text='CANCELAR', background_color=(0.7, 0.1, 0.1, 1))
        btn_volver.bind(on_press=self.volver)
        botones_layout.add_widget(btn_volver)

        form_container.add_widget(botones_layout)

        scroll_view.add_widget(form_container)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

    def precargar_datos(self):
        """Precarga los datos del combate en los campos del formulario"""
        if not self.combate_data:
            return
            
        print(f"[ActualizarCombateScreen] Precargando datos del combate: {self.combate_data}")
        
        data = self.combate_data
        
        # Competidor 1 (Rojo)
        self.competidor1_input.text = str(data.get('competidor1', '') or '')
        if data.get('fecha_nac1'):
            self.fecha_nac1_selector.set_date(data['fecha_nac1'])
        self.peso1_input.text = str(data.get('peso1', '') or '')
        self.sexo1_input.text = str(data.get('sexo1', '') or '')
        self.nacionalidad1_input.text = str(data.get('nacionalidad1', '') or '')
        
        # Competidor 2 (Azul)
        self.competidor2_input.text = str(data.get('competidor2', '') or '')
        if data.get('fecha_nac2'):
            self.fecha_nac2_selector.set_date(data['fecha_nac2'])
        self.peso2_input.text = str(data.get('peso2', '') or '')
        self.sexo2_input.text = str(data.get('sexo2', '') or '')
        self.nacionalidad2_input.text = str(data.get('nacionalidad2', '') or '')
        
        # Datos del combate
        if data.get('fecha'):
            self.fecha_combate_selector.set_date(data['fecha'])
        if data.get('hora'):
            self.hora_combate_selector.set_time(data['hora'])
        self.area_input.text = str(data.get('area', data.get('categoria', '')) or '')
        
        if data.get('categoria'):
            self.categoria_peso_selector.set_category(data['categoria'])
        
        if data.get('num_rounds'):
            self.rounds_selector.set_rounds(data['num_rounds'])
        
        if data.get('duracion_round'):
            self.duracion_round_selector.set_duration_from_seconds(data['duracion_round'])
        
        if data.get('duracion_descanso'):
            self.duracion_descanso_selector.set_duration_from_seconds(data['duracion_descanso'])
        
        # Jueces
        self.arbitro_nombre_input.text = str(data.get('arbitro_nombre', '') or '')
        self.arbitro_apellidos_input.text = str(data.get('arbitro_Apellidos', '') or '')
        self.juez1_nombre_input.text = str(data.get('juez1_nombre', '') or '')
        self.juez1_apellidos_input.text = str(data.get('juez1_Apellidos', '') or '')
        self.juez2_nombre_input.text = str(data.get('juez2_nombre', '') or '')
        self.juez2_apellidos_input.text = str(data.get('juez2_Apellidos', '') or '')
        self.juez3_nombre_input.text = str(data.get('juez3_nombre', '') or '')
        self.juez3_apellidos_input.text = str(data.get('juez3_Apellidos', '') or '')

    def update_background(self, *args):
        self.background_rect.size = Window.size
        self.background_rect.pos = self.pos

    def mostrar_mensaje(self, titulo, mensaje, on_dismiss=None):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))

        popup_width = dp(450) - 2 * dp(20)

        lbl_mensaje = Label(
            text=mensaje,
            color=(0.2, 0.6, 1, 1),
            font_size=sp(20),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80),
            text_size=(popup_width, None),
            shorten=False,
            mipmap=True,
            line_height=1.2
        )
        lbl_mensaje.bind(texture_size=lbl_mensaje.setter('size'))
        content.add_widget(lbl_mensaje)

        btn_aceptar = Button(
            text='ACEPTAR',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=sp(18))

        popup = Popup(
            title=titulo,
            title_color=(0.2, 0.6, 1, 1),
            title_size=sp(22),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=(dp(450), dp(250)),
            separator_height=0,
            background=''
        )

        with popup.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            popup.rect = RoundedRectangle(pos=popup.pos, size=popup.size, radius=[dp(15)])

        def update_popup_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

        popup.bind(pos=update_popup_rect, size=update_popup_rect)
        
        if on_dismiss:
            popup.bind(on_dismiss=on_dismiss)

        btn_aceptar.bind(on_press=popup.dismiss)
        content.add_widget(btn_aceptar)

        popup.open()

    def mostrar_popup_campos_faltantes(self, campos_faltantes):
        content = ScrollView()
        lista_campos = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20), size_hint_y=None)
        lista_campos.bind(minimum_height=lista_campos.setter('height'))

        titulo_label = Label(
            text='Campos Obligatorios Faltantes:',
            font_size=sp(20),
            color=(0.2, 0.6, 1, 1),
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        lista_campos.add_widget(titulo_label)

        for campo in campos_faltantes:
            label_campo = Label(
                text=f"• {campo}",
                font_size=sp(18),
                color=(0.1, 0.1, 0.2, 1),
                size_hint_y=None,
                height=dp(30)
            )
            lista_campos.add_widget(label_campo)

        content.add_widget(lista_campos)

        popup = Popup(
            title='¡Atención!',
            title_color=(0.2, 0.6, 1, 1),
            title_size=sp(22),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=(dp(500), dp(400)),
            separator_height=0,
            background=''
        )

        with popup.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            popup.rect = RoundedRectangle(pos=popup.pos, size=popup.size, radius=[dp(15)])

        def update_popup_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

        popup.bind(pos=update_popup_rect, size=update_popup_rect)

        btn_cerrar = Button(
            text='CERRAR',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=sp(18))
        btn_cerrar.bind(on_press=popup.dismiss)
        lista_campos.add_widget(btn_cerrar)

        popup.open()

    def validar_campos(self):
        """Valida los campos obligatorios"""
        required_fields = [
            (self.competidor1_input, "Nombre(s) del Competidor Rojo"),
            (self.peso1_input, "Peso del Competidor Rojo (kg)"),
            (self.sexo1_input, "Sexo del Competidor Rojo"),
            (self.competidor2_input, "Nombre(s) del Competidor Azul"),
            (self.peso2_input, "Peso del Competidor Azul (kg)"),
            (self.sexo2_input, "Sexo del Competidor Azul"),
            (self.area_input, "Área de Combate"),
            (self.arbitro_nombre_input, "Nombre(s) del Árbitro Central"),
            (self.arbitro_apellidos_input, "Apellidos del Árbitro Central"),
        ]

        campos_faltantes = [msg for campo, msg in required_fields if not campo.text.strip()]
        
        if campos_faltantes:
            self.mostrar_popup_campos_faltantes(campos_faltantes)
            return False

        # Validar pesos numéricos
        try:
            float(self.peso1_input.text)
            float(self.peso2_input.text)
        except ValueError:
            self.mostrar_mensaje("Error", "Los pesos deben ser números válidos")
            return False

        return True

    def construir_payload(self):
        """Construye el payload para la API"""
        # Construir fecha y hora del combate en formato ISO
        fecha_combate = self.fecha_combate_selector.get_selected_date()
        hora_combate = self.hora_combate_selector.get_selected_time()
        hora_combate_iso = f"{fecha_combate.isoformat()}T{hora_combate.strftime('%H:%M:%S')}"
        
        # Fecha nacimiento competidores
        fecha_nac1 = self.fecha_nac1_selector.get_selected_date().isoformat()
        fecha_nac2 = self.fecha_nac2_selector.get_selected_date().isoformat()
        
        payload = {
            "competidorRojo": {
                "nombres": self.competidor1_input.text.strip(),
                "sexo": self.sexo1_input.text.strip(),
                "pesoKg": float(self.peso1_input.text),
                "fechaNacimiento": fecha_nac1
            },
            "competidorAzul": {
                "nombres": self.competidor2_input.text.strip(),
                "sexo": self.sexo2_input.text.strip(),
                "pesoKg": float(self.peso2_input.text),
                "fechaNacimiento": fecha_nac2
            },
            "area": self.area_input.text.strip(),
            "numeroRound": self.rounds_selector.get_selected_rounds(),
            "duracionRound": self.duracion_round_selector.get_api_format(),
            "duracionDescanso": self.duracion_descanso_selector.get_api_format(),
            "horaCombate": hora_combate_iso,
            "estado": self.combate_data.get('estado', 'PENDIENTE') if self.is_edit_mode else 'PENDIENTE',
            "jueces": {
                "arbitroCentral": {
                    "nombres": self.arbitro_nombre_input.text.strip(),
                    "apellidos": self.arbitro_apellidos_input.text.strip()
                },
                "juez1": {
                    "nombres": self.juez1_nombre_input.text.strip(),
                    "apellidos": self.juez1_apellidos_input.text.strip()
                },
                "juez2": {
                    "nombres": self.juez2_nombre_input.text.strip(),
                    "apellidos": self.juez2_apellidos_input.text.strip()
                },
                "juez3": {
                    "nombres": self.juez3_nombre_input.text.strip(),
                    "apellidos": self.juez3_apellidos_input.text.strip()
                }
            }
        }
        
        # Agregar torneo_id si existe
        if self.is_edit_mode and self.combate_data.get('torneo_id'):
            payload['idTorneo'] = self.combate_data['torneo_id']
        
        return payload

    def guardar_combate(self, instance):
        """Guarda o actualiza el combate"""
        if not self.validar_campos():
            return
        
        if self.is_edit_mode:
            self.actualizar_combate()
        else:
            self.crear_combate()

    def crear_combate(self):
        """Crea un nuevo combate"""
        if not api:
            self.mostrar_mensaje("Error", "Cliente API no disponible")
            return
        
        payload = self.construir_payload()
        
        def _do_create():
            try:
                result = api.create_combate(payload)
                if result:
                    Clock.schedule_once(lambda dt: self._on_create_success(result))
                else:
                    Clock.schedule_once(
                        lambda dt: self.mostrar_mensaje("Error", "No se pudo crear el combate")
                    )
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self.mostrar_mensaje("Error", f"Error al crear: {str(e)}")
                )
        
        thread = Thread(target=_do_create)
        thread.daemon = True
        thread.start()

    def _on_create_success(self, result):
        """Callback cuando se crea exitosamente"""
        self.mostrar_mensaje(
            "¡Combate creado!",
            f"El combate entre {self.competidor1_input.text} y {self.competidor2_input.text} ha sido creado con éxito",
            on_dismiss=lambda x: self.volver(None)
        )

    def actualizar_combate(self):
        """Actualiza un combate existente"""
        if not api:
            self.mostrar_mensaje("Error", "Cliente API no disponible")
            return
        
        combate_id = self.combate_data.get('id')
        if not combate_id:
            self.mostrar_mensaje("Error", "ID del combate no encontrado")
            return
        
        # Para actualizar, usamos un payload más simple
        # ya que el endpoint PUT solo acepta ciertos campos
        payload = {
            "area": self.area_input.text.strip(),
            "numeroRound": self.rounds_selector.get_selected_rounds(),
            "duracionRound": self.duracion_round_selector.get_api_format(),
            "duracionDescanso": self.duracion_descanso_selector.get_api_format(),
            "estado": self.combate_data.get('estado', 'PENDIENTE')
        }
        
        def _do_update():
            try:
                result = api.update_combate(combate_id, payload)
                if result:
                    Clock.schedule_once(lambda dt: self._on_update_success())
                else:
                    Clock.schedule_once(
                        lambda dt: self.mostrar_mensaje("Error", "No se pudo actualizar el combate")
                    )
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self.mostrar_mensaje("Error", f"Error al actualizar: {str(e)}")
                )
        
        thread = Thread(target=_do_update)
        thread.daemon = True
        thread.start()

    def _on_update_success(self):
        """Callback cuando se actualiza exitosamente"""
        # Construir los nuevos datos para el callback
        nuevos_datos = {
            "area": self.area_input.text.strip(),
            "num_rounds": self.rounds_selector.get_selected_rounds(),
            "duracion_round": self.duracion_round_selector.get_selected_duration(),
            "duracion_descanso": self.duracion_descanso_selector.get_selected_duration(),
        }
        
        # Llamar al callback si existe
        if self.on_save_callback:
            self.on_save_callback(self.combate_data, nuevos_datos)
        
        self.mostrar_mensaje(
            "¡Combate actualizado!",
            f"El combate #{self.combate_data.get('numero', '')} ha sido actualizado con éxito",
            on_dismiss=lambda x: self.volver(None)
        )

    def volver(self, instance):
        """Vuelve a la pantalla anterior"""
        app = App.get_running_app()
        
        # Intentar volver a combates_anteriores o a la pantalla principal
        if app.root.has_screen('combates_anteriores'):
            app.root.current = 'combates_anteriores'
        elif app.root.has_screen('torneos_anteriores'):
            app.root.current = 'torneos_anteriores'
        else:
            app.root.current = 'ini'