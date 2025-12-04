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
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.spinner import Spinner
from kivy.properties import StringProperty, ObjectProperty
from kivy.utils import platform
from datetime import datetime, date
import calendar
from threading import Thread
from api_client import api


# ------------------ UTILIDADES RESPONSIVE ------------------
class ResponsiveHelper:
    @staticmethod
    def is_mobile():
        return platform in ['android', 'ios']
    
    @staticmethod
    def is_desktop():
        return platform in ['win', 'linux', 'macosx']
    
    @staticmethod
    def get_form_width():
        """Retorna el ancho del formulario según el tamaño de ventana"""
        width = Window.width
        if width < 600:
            return 0.95  # 95% en pantallas muy pequeñas
        elif width < 900:
            return 0.85  # 85% en pantallas pequeñas
        elif width < 1200:
            return 0.7  # 70% en pantallas medianas
        else:
            return 0.6  # 60% en pantallas grandes
    
    @staticmethod
    def get_font_size(base_size):
        width = Window.width
        if width < 600:
            return sp(base_size * 0.8)
        elif width < 900:
            return sp(base_size * 0.9)
        return sp(base_size)
    
    @staticmethod
    def get_popup_size():
        """Retorna tamaño apropiado para popups"""
        width = Window.width
        height = Window.height
        if width < 600:
            return (width * 0.9, min(height * 0.5, dp(350)))
        else:
            return (min(width * 0.7, dp(500)), min(height * 0.5, dp(400)))


# ------------------ SELECTOR DE FECHA RESPONSIVE ------------------
class DateSelector(BoxLayout):
    selected_date = ObjectProperty(date.today())
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(55)
        
        # Años (desde el actual hasta 10 años adelante)
        current_year = datetime.now().year
        self.year_spinner = Spinner(
            text=str(current_year),
            values=[str(y) for y in range(current_year, current_year + 11)],
            size_hint=(0.3, 1),
            font_size=ResponsiveHelper.get_font_size(18),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1)
        )
        
        # Meses en español
        meses_espanol = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        self.month_spinner = Spinner(
            text=meses_espanol[datetime.now().month - 1],
            values=meses_espanol,
            size_hint=(0.4, 1),
            font_size=ResponsiveHelper.get_font_size(18),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1))
        
        # Días (se actualizará según mes y año)
        self.day_spinner = Spinner(
            text=str(datetime.now().day),
            values=[],
            size_hint=(0.3, 1),
            font_size=ResponsiveHelper.get_font_size(18),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1))
        
        self.add_widget(self.day_spinner)
        self.add_widget(self.month_spinner)
        self.add_widget(self.year_spinner)
        
        # Actualizar días iniciales
        self.update_days()
        
        # Bind para actualizar días cuando cambia mes o año
        self.month_spinner.bind(text=self.update_days_on_change)
        self.year_spinner.bind(text=self.update_days_on_change)
        Window.bind(on_resize=self.on_window_resize)
        
    def on_window_resize(self, instance, width, height):
        self.year_spinner.font_size = ResponsiveHelper.get_font_size(18)
        self.month_spinner.font_size = ResponsiveHelper.get_font_size(18)
        self.day_spinner.font_size = ResponsiveHelper.get_font_size(18)
        self.height = dp(55)
        
    def update_days_on_change(self, *args):
        self.update_days()
        self.get_selected_date()
        
    def update_days(self):
        month = self.month_spinner.text
        year = self.year_spinner.text
        
        if month and year:
            # Convertir mes en español a número
            meses_espanol = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            month_num = meses_espanol.index(month) + 1
            year_num = int(year)
            _, num_days = calendar.monthrange(year_num, month_num)
            
            current_day = int(self.day_spinner.text) if self.day_spinner.text.isdigit() else 1
            days = [str(d) for d in range(1, num_days + 1)]
            self.day_spinner.values = days
            
            # Asegurarse de que el día seleccionado sea válido
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


# ------------------ SELECTOR DE HORA RESPONSIVE ------------------
class TimeSelector(BoxLayout):
    selected_time = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(55)
        
        # Horas
        current_hour = datetime.now().hour
        self.hour_spinner = Spinner(
            text=f"{current_hour:02d}",
            values=[f"{h:02d}" for h in range(0, 24)],
            size_hint=(0.45, 1),
            font_size=ResponsiveHelper.get_font_size(18),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1)
        )
        
        # Minutos
        current_minute = (datetime.now().minute // 5) * 5  # Redondear a múltiplos de 5
        self.minute_spinner = Spinner(
            text=f"{current_minute:02d}",
            values=[f"{m:02d}" for m in range(0, 60, 5)],
            size_hint=(0.45, 1),
            font_size=ResponsiveHelper.get_font_size(18),
            background_color=(0.1, 0.4, 0.7, 0.9),
            color=(1, 1, 1, 1))
        
        self.add_widget(self.hour_spinner)
        self.add_widget(Label(
            text=":",
            size_hint=(0.1, 1),
            font_size=ResponsiveHelper.get_font_size(24),
            color=(0.1, 0.4, 0.7, 1)
        ))
        self.add_widget(self.minute_spinner)
        
        # Configurar hora inicial
        self.get_selected_time()
        
        # Bind para actualizar cuando cambia
        self.hour_spinner.bind(text=self.update_time)
        self.minute_spinner.bind(text=self.update_time)
        Window.bind(on_resize=self.on_window_resize)
        
    def on_window_resize(self, instance, width, height):
        self.hour_spinner.font_size = ResponsiveHelper.get_font_size(18)
        self.minute_spinner.font_size = ResponsiveHelper.get_font_size(18)
        self.height = dp(55)
        
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


# ------------------ TEXT INPUT REDONDEADO RESPONSIVE ------------------
class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_active = ""
        self.background_color = (0, 0, 0, 0)  # Fondo transparente
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(55)
        self.padding = [dp(15), dp(15), dp(15), dp(15)]
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.color = (1, 1, 1, 1)  # Texto blanco
        self.hint_text_color = (0.9, 0.9, 0.9, 0.8)
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
                radius=[dp(10)]
            )

        self.bind(pos=self._update_rects, size=self._update_rects)
        Window.bind(on_resize=self.on_window_resize)

    def _update_rects(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.pos[0]+dp(2), self.pos[1]+dp(2))
        self.border_rect.size = (self.size[0]-dp(4), self.size[1]-dp(4))
    
    def on_window_resize(self, instance, width, height):
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.height = dp(55)

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
                    radius=[dp(10)]
                )
        else:
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
                    radius=[dp(10)]
                )
            self._update_rects()


# ------------------ BOTÓN HOVER RESPONSIVE ------------------
class HoverButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.1, 0.4, 0.7, 1)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.bold = True
        self.border_radius = dp(12)

        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.border_radius]
            )

        self.bind(pos=self.update_rect, size=self.update_rect)
        Window.bind(on_resize=self.on_window_resize)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_window_resize(self, instance, width, height):
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.height = dp(50)


# ------------------ PANTALLA CREAR TORNEO RESPONSIVE ------------------
class CrearTorneoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._submitting = False
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

    def build_ui(self):
        self.clear_widgets()
        
        # ScrollView principal
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=dp(10),
            scroll_type=['bars', 'content']
        )
        
        # Layout principal
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(30), dp(20), dp(30)],
            spacing=dp(15),
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))

        # Fondo
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.background_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self.update_background, pos=self.update_background)

        # Espaciador superior
        top_spacer_height = max(dp(20), Window.height * 0.03)
        main_layout.add_widget(Widget(size_hint_y=None, height=top_spacer_height))

        # Contenedor del formulario centrado
        form_container = BoxLayout(
            orientation='vertical',
            size_hint=(ResponsiveHelper.get_form_width(), None),
            pos_hint={'center_x': 0.5},
            spacing=dp(15)
        )
        form_container.bind(minimum_height=form_container.setter('height'))

        # Logo responsive
        logo_height = min(dp(120), Window.height * 0.15)
        logo = Image(
            source="Imagen5-Photoroom.png",
            size_hint=(1, None),
            height=logo_height,
            allow_stretch=True,
            keep_ratio=True
        )
        form_container.add_widget(logo)

        # Título
        titulo = Label(
            text='CREAR TORNEO',
            font_size=ResponsiveHelper.get_font_size(32),
            color=(0.1, 0.4, 0.7, 1),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        form_container.add_widget(titulo)

        # Espaciador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # Función para crear campos
        def crear_campo(texto, hint_text=None, widget=None):
            campo_layout = BoxLayout(
                orientation='vertical',
                spacing=dp(8),
                size_hint_y=None
            )
            campo_layout.bind(minimum_height=campo_layout.setter('height'))
            
            label = Label(
                text=texto,
                font_size=ResponsiveHelper.get_font_size(18),
                color=(0.1, 0.1, 0.2, 1),
                size_hint_y=None,
                height=dp(30),
                halign='left'
            )
            label.bind(size=label.setter('text_size'))
            campo_layout.add_widget(label)
            
            if widget:
                campo_layout.add_widget(widget)
            else:
                input_field = RoundedTextInput(hint_text=hint_text)
                campo_layout.add_widget(input_field)
                return campo_layout, input_field
            return campo_layout, widget

        # Campos del formulario
        nombre_torneo_layout, self.nombre_torneo_input = crear_campo(
            'Nombre del Torneo',
            'Ingresa el nombre del torneo'
        )
        form_container.add_widget(nombre_torneo_layout)

        # Selector de fecha
        self.date_selector = DateSelector()
        fecha_layout, _ = crear_campo('Fecha', widget=self.date_selector)
        form_container.add_widget(fecha_layout)

        ubicacion_layout, self.ubicacion_input = crear_campo('Sede', 'Lugar del torneo')
        form_container.add_widget(ubicacion_layout)

        # Selector de hora de inicio
        self.time_start_selector = TimeSelector()
        hora_inicio_layout, _ = crear_campo('Hora de Inicio', widget=self.time_start_selector)
        form_container.add_widget(hora_inicio_layout)

        # Selector de hora de término
        self.time_end_selector = TimeSelector()
        hora_termino_layout, _ = crear_campo('Hora de Término', widget=self.time_end_selector)
        form_container.add_widget(hora_termino_layout)

        # Espaciador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(15)))

        # Botones responsive
        botones_layout = BoxLayout(
            orientation='horizontal' if Window.width > 600 else 'vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(50) if Window.width > 600 else dp(110)
        )

        btn_crear = HoverButton(text='CREAR TORNEO')
        btn_crear.bind(on_press=self.crear_torneo)
        botones_layout.add_widget(btn_crear)

        btn_volver = HoverButton(text='VOLVER')
        btn_volver.canvas.before.clear()
        with btn_volver.canvas.before:
            Color(0.7, 0.1, 0.1, 1)
            btn_volver.rect = RoundedRectangle(
                pos=btn_volver.pos,
                size=btn_volver.size,
                radius=[btn_volver.border_radius]
            )
        btn_volver.bind(on_press=self.volver)
        botones_layout.add_widget(btn_volver)

        form_container.add_widget(botones_layout)

        main_layout.add_widget(form_container)
        
        # Espaciador inferior
        main_layout.add_widget(Widget(size_hint_y=None, height=dp(30)))

        scroll_view.add_widget(main_layout)
        self.add_widget(scroll_view)

    def update_background(self, instance, value):
        self.background_rect.size = instance.size
        self.background_rect.pos = instance.pos

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)

    def mostrar_mensaje(self, titulo, mensaje, on_close=None):
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20)
        )

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

        btn_aceptar = Button(
            text='ACEPTAR',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(18)
        )

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

        with popup.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            popup.rect = RoundedRectangle(
                pos=popup.pos,
                size=popup.size,
                radius=[dp(15)]
            )

        def update_popup_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

        popup.bind(pos=update_popup_rect, size=update_popup_rect)

        def _close_and_callback(*_):
            popup.dismiss()
            if callable(on_close):
                on_close()

        btn_aceptar.bind(on_press=_close_and_callback)
        content.add_widget(btn_aceptar)
        popup.open()

    # ---- helpers ----
    def _dt_iso(self, fecha: date, hora) -> str:
        """Fecha y hora"""
        dt = datetime(year=fecha.year, month=fecha.month, day=fecha.day, hour=hora.hour, minute=hora.minute, second= 0 , microsecond= 0)

        return dt.strftime('%Y-%m-%dT%H:%M:%S')
    
    def _get_admin_id(self):
        """Intenta extraer el id del admin desde app.auth."""
        app = App.get_running_app()
        if not hasattr(app, 'auth') or not app.auth:
            return None
        admin = app.auth.get('admin') or {}

        return admin.get('idAdministrador') or admin.get('id') or admin.get('adminId')
    

    def mostrar_popup_campos_faltantes(self, campos_faltantes):
        content = ScrollView()
        lista_campos = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None
        )
        lista_campos.bind(minimum_height=lista_campos.setter('height'))

        titulo_label = Label(
            text='Campos Obligatorios Faltantes:',
            font_size=ResponsiveHelper.get_font_size(20),
            color=(0.5, 0.8, 1, 1),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        lista_campos.add_widget(titulo_label)

        for mensaje in campos_faltantes:
            label_campo = Label(
                text=f"• {mensaje}",
                font_size=ResponsiveHelper.get_font_size(16),
                color=(0.5, 0.8, 1, 1),
                size_hint_y=None,
                height=dp(35),
                halign='left'
            )
            label_campo.bind(size=label_campo.setter('text_size'))
            lista_campos.add_widget(label_campo)

        content.add_widget(lista_campos)

        popup_size = ResponsiveHelper.get_popup_size()
        popup = Popup(
            title='¡Atención!',
            title_color=(1, 1, 1, 1),
            title_size=ResponsiveHelper.get_font_size(22),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=popup_size,
            separator_height=0,
            background=''
        )

        with popup.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            popup.rect = RoundedRectangle(
                pos=popup.pos,
                size=popup.size,
                radius=[dp(15)]
            )

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
            font_size=ResponsiveHelper.get_font_size(18)
        )
        btn_cerrar.bind(on_press=popup.dismiss)
        lista_campos.add_widget(btn_cerrar)

        popup.open()

    def crear_torneo(self, instance):
        required_fields = [
            (self.nombre_torneo_input, "Nombre del torneo"),
            (self.ubicacion_input, "Sede del torneo")
        ]
        faltantes = [msg for campo, msg in required_fields if not campo.text.strip()]
        if faltantes:
            self.mostrar_popup_campos_faltantes(faltantes)
            return

        fecha = self.date_selector.get_selected_date()
        hora_inicio = self.time_start_selector.get_selected_time()
        hora_termino = self.time_end_selector.get_selected_time()

        if hora_inicio >= hora_termino:
            self.mostrar_mensaje("Error", "La hora de término debe ser posterior a la de inicio")
            return

  
        fecha_hora_iso = self._dt_iso(fecha, hora_inicio)
        admin_id = self._get_admin_id()
        payload = {
            "nombre": self.nombre_torneo_input.text.strip(),  
            "fechaHora": fecha_hora_iso,
            "sede": self.ubicacion_input.text.strip(),
            "estado": "PROGRAMADO",  
            "administrador": { "idAdministrador": admin_id }  
        }

        if self._submitting:
            return
        self._submitting = True
        instance.disabled = True
        original_text = instance.text
        instance.text = "Creando..."

        def _task():
            try:
                resp = api.post_json("/apiTorneos/torneo", payload)
                status = resp.status_code
                if status in (200, 201):
                    try:
                        data = resp.json()
                    except Exception:
                        data = None

                    def _ok(dt):
                        nombre = self.nombre_torneo_input.text.strip()
                        self.mostrar_mensaje(
                            "¡Torneo creado!",
                            f"El torneo {self.nombre_torneo_input.text} ha sido creado con éxito\n"
                            f"Fecha: {fecha.strftime('%d/%m/%Y')}  "
                            f"Hora: {hora_inicio.strftime('%H:%M')} - {hora_termino.strftime('%H:%M')}"
                        )
                        # limpiar campos
                        self.nombre_torneo_input.text = ""
                        self.ubicacion_input.text = ""
                        
                        def go_home():
                            App.get_running_app().root.current = 'ini'

                        self.mostrar_mensaje(
                            "¡Torneo creado!",
                            f"El torneo {nombre} ha sido creado con éxito\n"
                            f"Fecha: {fecha.strftime('%d/%m/%Y')}  "
                            f"Hora: {hora_inicio.strftime('%H:%M')} - {hora_termino.strftime('%H:%M')}",
                            on_close=go_home
                        )
                        
                    Clock.schedule_once(_ok, 0)

                else:
                    try:
                        err = resp.json().get("message", f"Error del servidor ({status})")
                    except Exception:
                        err = f"Error del servidor ({status})"
                    Clock.schedule_once(lambda dt, m=err: self.mostrar_mensaje("Error", m), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt, m=str(e): self.mostrar_mensaje("Error", f"No se pudo crear el torneo.\n{m}"), 0)
            finally:
                def _reset(dt):
                    self._submitting = False
                    instance.disabled = False
                    instance.text = original_text
                Clock.schedule_once(_reset, 0)

        Thread(target=_task, daemon=True).start()

    def volver(self, instance):
        App.get_running_app().root.current = 'ini'

    def update_background(self, instance, value):
        self.background_rect.size = instance.size
        self.background_rect.pos = instance.pos

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)