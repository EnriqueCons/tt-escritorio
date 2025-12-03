from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp
from kivy.properties import StringProperty
from kivy.utils import platform
from kivy.clock import Clock
from kivy.app import App
from api_client import api
from session_manager import session


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
            return 0.95
        elif width < 900:
            return 0.85
        elif width < 1200:
            return 0.7
        else:
            return 0.55
    
    @staticmethod
    def get_font_size(base_size):
        """Retorna tamaño de fuente responsive"""
        width = Window.width
        if width < 600:
            return sp(base_size * 0.7)
        elif width < 900:
            return sp(base_size * 0.85)
        return sp(base_size)
    
    @staticmethod
    def get_button_height():
        """Retorna altura de botones responsive"""
        width = Window.width
        if width < 600:
            return dp(45)
        return dp(50)
    
    @staticmethod
    def get_logo_height():
        """Retorna altura del logo responsive"""
        width = Window.width
        height = Window.height
        if width < 600:
            return dp(80)
        elif width < 900:
            return dp(100)
        return min(dp(120), height * 0.12)
    
    @staticmethod
    def get_popup_size():
        """Retorna tamaño apropiado para popups"""
        width = Window.width
        height = Window.height
        if width < 600:
            return (width * 0.9, min(height * 0.4, dp(300)))
        else:
            return (min(width * 0.6, dp(450)), min(height * 0.35, dp(250)))


# ------------------ DISPLAY DE DATOS RESPONSIVE ------------------
class ResponsiveDataDisplay(BoxLayout):
    text = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(50)  # Altura fija
        self.spacing = 0
        
        # Contenedor con fondo y sombra
        with self.canvas.before:
            # Sombra sutil
            Color(0.05, 0.2, 0.35, 0.15)
            self.shadow = RoundedRectangle(
                size=self.size,
                pos=(self.pos[0] + dp(2), self.pos[1] - dp(2)),
                radius=[dp(12)]
            )
            # Fondo principal azul claro
            Color(0.2, 0.6, 1, 0.15)
            self.rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[dp(12)]
            )
            # Borde azul
            Color(0.2, 0.6, 1, 0.4)
            self.border = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[dp(12)]
            )
        
        # Label para mostrar el texto - CENTRADO
        self.label = Label(
            text=self.text,
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.1, 0.4, 0.7, 1),
            halign='center',  # Centrado horizontal
            valign='middle',   # Centrado vertical
            size_hint=(1, 1),
            bold=True
        )
        
        # Vincular text_size al tamaño del label para que el centrado funcione
        self.label.bind(size=self._update_label_text_size)
        
        self.add_widget(self.label)
        self.bind(
            size=self._update_rect,
            pos=self._update_rect,
            text=self._update_text
        )
        
        Window.bind(on_resize=self.on_window_resize)
    
    def _update_label_text_size(self, instance, value):
        """Actualiza el text_size del label para mantener el centrado"""
        self.label.text_size = (instance.width, instance.height)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        self.shadow.pos = (instance.pos[0] + dp(2), instance.pos[1] - dp(2))
        self.shadow.size = instance.size
        self.border.pos = instance.pos
        self.border.size = instance.size
    
    def _update_text(self, instance, value):
        self.label.text = value
    
    def on_window_resize(self, instance, width, height):
        self.label.font_size = ResponsiveHelper.get_font_size(18)


# ------------------ BOTÓN HOVER RESPONSIVE ------------------
class HoverButton(Button):
    def __init__(self, **kwargs):
        bg_color = kwargs.pop('bg_color', (0.1, 0.4, 0.7, 1))
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.size_hint_y = None
        self.height = ResponsiveHelper.get_button_height()
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.border_radius = dp(12)

        with self.canvas.before:
            Color(*bg_color)
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
        self.height = ResponsiveHelper.get_button_height()


# ------------------ PANTALLA VER INFORMACIÓN ------------------
class VerInfoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.admin_data = None
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

    def on_pre_enter(self):
        """Se ejecuta antes de mostrar la pantalla"""
        self.cargar_datos_administrador()

    def cargar_datos_administrador(self):
        """Carga los datos del administrador desde el backend"""
        try:
            # Primero intentar obtener de la app
            app = App.get_running_app()
            
            # Si no hay sesión en SessionManager, intentar recuperarla de app.auth
            if not session.is_logged_in() and hasattr(app, 'auth') and app.auth:
                session.set_session_from_app(app)
            
            # Verificar si hay sesión activa
            if not session.is_logged_in():
                self.mostrar_mensaje("Error", "No hay sesión activa. Por favor inicia sesión.")
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'inicio_sesion'), 2)
                return
            
            admin_id = session.get_admin_id()
            print(f"[VerInfoScreen] Cargando datos del administrador ID: {admin_id}")
            
            # Obtener datos actualizados del administrador desde la API
            self.admin_data = api.get_administrador_by_id(admin_id)
            
            # Actualizar la sesión con los datos más recientes
            session.update_admin_data(self.admin_data)
            
            # Actualizar la interfaz con los datos
            self.actualizar_campos_ui()
            
            print(f"[VerInfoScreen] Datos cargados exitosamente")
            
        except Exception as e:
            print(f"[VerInfoScreen] Error al cargar datos: {e}")
            self.mostrar_mensaje("Error", f"No se pudieron cargar los datos: {str(e)}")
            # Si hay error, mostrar datos en caché de la sesión
            self.mostrar_datos_cache()

    def mostrar_datos_cache(self):
        """Muestra los datos en caché de la sesión si hay error al cargar del backend"""
        cached_data = session.get_admin_data()
        if cached_data:
            self.admin_data = cached_data
            self.actualizar_campos_ui()
            print("[VerInfoScreen] Mostrando datos en caché")

    def actualizar_campos_ui(self):
        """Actualiza los campos de la interfaz con los datos del administrador"""
        if not self.admin_data:
            return
        
        # Actualizar cada campo
        if hasattr(self, 'nombres_display'):
            self.nombres_display.text = self.admin_data.get('nombreAdministrador', 'N/A')
        
        if hasattr(self, 'apellidos_display'):
            paterno = self.admin_data.get('paternoAdministrador', '')
            materno = self.admin_data.get('maternoAdministrador', '')
            apellidos = f"{paterno} {materno}".strip()
            self.apellidos_display.text = apellidos if apellidos else 'N/A'
        
        if hasattr(self, 'usuario_display'):
            self.usuario_display.text = self.admin_data.get('usuarioAdministrador', 'N/A')
        
        if hasattr(self, 'correo_display'):
            self.correo_display.text = self.admin_data.get('correoAdministrador', 'N/A')

    def build_ui(self):
        self.clear_widgets()

        # Layout principal
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(15), dp(10)],
            spacing=dp(8)
        )
        
        # Fondo de la pantalla
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.background_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        main_layout.bind(
            size=lambda instance, value: setattr(self.background_rect, 'size', value),
            pos=lambda instance, value: setattr(self.background_rect, 'pos', value)
        )

        # Logo responsive
        logo_height = ResponsiveHelper.get_logo_height()
        logo = Image(
            source="Imagen5-Photoroom.png",
            size_hint=(1, None),
            height=logo_height,
            pos_hint={'center_x': 0.5},
            fit_mode="contain"
        )
        main_layout.add_widget(logo)

        # ScrollView para el contenido
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=dp(10),
            bar_color=[0.2, 0.6, 1, 0.8],
            bar_inactive_color=[0.2, 0.6, 1, 0.4]
        )

        # Contenedor scrolleable
        scroll_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[0, dp(10)]
        )
        scroll_container.bind(minimum_height=scroll_container.setter('height'))

        # Contenedor del formulario centrado
        form_container = BoxLayout(
            orientation='vertical',
            size_hint=(ResponsiveHelper.get_form_width(), None),
            spacing=dp(10),
            padding=[dp(15), dp(10)],
            pos_hint={'center_x': 0.5}
        )
        form_container.bind(minimum_height=form_container.setter('height'))

        # Título con diseño mejorado
        titulo = Label(
            text='MI PERFIL',
            font_size=ResponsiveHelper.get_font_size(36),
            color=(0.1, 0.4, 0.7, 1),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        form_container.add_widget(titulo)

        # Espaciador reducido
        form_container.add_widget(Widget(size_hint_y=None, height=dp(5)))

        # Función para crear campos
        def crear_campo(etiqueta, valor_inicial="Cargando..."):
            campo_layout = BoxLayout(
                orientation='vertical',
                spacing=dp(4),
                size_hint_y=None
            )
            campo_layout.bind(minimum_height=campo_layout.setter('height'))

            # Etiqueta del campo
            lbl_etiqueta = Label(
                text=etiqueta,
                font_size=ResponsiveHelper.get_font_size(18),
                color=(0.1, 0.1, 0.2, 1),
                size_hint_y=None,
                height=dp(25),
                bold=True,
                halign='left'
            )
            lbl_etiqueta.bind(size=lbl_etiqueta.setter('text_size'))
            campo_layout.add_widget(lbl_etiqueta)

            # Display de datos responsivo
            data_display = ResponsiveDataDisplay(text=valor_inicial)
            campo_layout.add_widget(data_display)
            
            return campo_layout, data_display

        # Campos de información
        campos_info = [
            ('Nombre(s)', 'Cargando...'),
            ('Apellidos', 'Cargando...'),
            ('Usuario', 'Cargando...'),
            ('Correo', 'Cargando...')
        ]

        for etiqueta, valor_inicial in campos_info:
            layout, display = crear_campo(etiqueta, valor_inicial)
            attr_name = etiqueta.lower().replace("(", "").replace(")", "").replace(" ", "_") + "_display"
            setattr(self, attr_name, display)
            form_container.add_widget(layout)

        # Espaciador reducido
        form_container.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # Botones responsive
        botones_layout = BoxLayout(
            orientation='horizontal' if Window.width > 800 else 'vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=ResponsiveHelper.get_button_height() if Window.width > 800 else ResponsiveHelper.get_button_height() * 2 + dp(15)
        )

        btn_actualizar = HoverButton(
            text='ACTUALIZAR',
            bg_color=(0.2, 0.6, 1, 1)
        )
        btn_actualizar.bind(on_press=self.actualizar_datos)

        btn_volver = HoverButton(
            text='VOLVER',
            bg_color=(0.7, 0.1, 0.1, 1)
        )
        btn_volver.bind(on_press=self.volver)

        botones_layout.add_widget(btn_actualizar)
        botones_layout.add_widget(btn_volver)
        form_container.add_widget(botones_layout)

        # Espaciador inferior reducido
        form_container.add_widget(Widget(size_hint_y=None, height=dp(10)))

        scroll_container.add_widget(form_container)
        scroll_view.add_widget(scroll_container)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)

    def actualizar_datos(self, instance):
        """Navega a la pantalla de actualización"""
        # Pasar los datos actuales a la pantalla de actualización
        if self.manager.has_screen('actualizar'):
            actualizar_screen = self.manager.get_screen('actualizar')
            if hasattr(actualizar_screen, 'set_admin_data'):
                actualizar_screen.set_admin_data(self.admin_data)
        
        self.manager.current = 'actualizar'
    
    def volver(self, instance):
        self.manager.current = 'ini'

    def mostrar_mensaje(self, titulo, mensaje):
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
            height=ResponsiveHelper.get_button_height(),
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
        btn_aceptar.bind(on_press=popup.dismiss)
        content.add_widget(btn_aceptar)
        popup.open()


# ------------------ APP DE PRUEBA ------------------
if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager
    
    # Para pruebas, establecer una sesión ficticia
    session.set_session(
        admin_id=1,
        admin_data={
            'idAdministrador': 1,
            'nombreAdministrador': 'Enrique Gabriel',
            'paternoAdministrador': 'Contreras',
            'maternoAdministrador': 'González',
            'usuarioAdministrador': 'Sbn Enrique',
            'correoAdministrador': 'enrique@gmail.com'
        }
    )
    
    class TestApp(App):
        def build(self):
            sm = ScreenManager()
            sm.add_widget(VerInfoScreen(name='ver_info'))
            return sm
    
    TestApp().run()