from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.app import App
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from api_client import api
from session_manager import session
from cuenta import VerInfoScreen

# ------------------ UTILIDADES RESPONSIVE ------------------
class ResponsiveHelper:
    @staticmethod
    def is_mobile():
        return platform in ['android', 'ios']
    
    @staticmethod
    def is_desktop():
        return platform in ['win', 'linux', 'macosx']
    
    @staticmethod
    def get_navbar_width():
        """Retorna el ancho del navbar según el tamaño de ventana"""
        width = Window.width
        if width < 600:
            return dp(60)  # Navbar colapsado en móvil
        elif width < 900:
            return dp(150)
        elif width < 1200:
            return dp(180)
        else:
            return dp(200)
    
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
            return dp(120)
        return min(dp(150), height * 0.15)
    
    @staticmethod
    def get_popup_size():
        """Retorna tamaño apropiado para popups"""
        width = Window.width
        height = Window.height
        if width < 600:
            return (width * 0.9, min(height * 0.4, dp(300)))
        else:
            return (min(width * 0.6, dp(450)), min(height * 0.35, dp(250)))
    
    @staticmethod
    def should_show_text():
        """Determina si se debe mostrar texto en botones del navbar"""
        return Window.width >= 600


# ------------------ BOTÓN HOVER RESPONSIVE ------------------
class HoverButton(Button):
    def __init__(self, **kwargs):
        # Extraer bg_color antes de llamar al constructor padre
        bg_color = kwargs.pop('bg_color', (0.1, 0.4, 0.7, 1))
        
        super().__init__(**kwargs)
        
        self.original_background_color = bg_color
        self.hover_background_color = (0.2, 0.5, 0.9, 1)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.size_hint_y = None
        self.height = ResponsiveHelper.get_button_height()
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.border_radius = dp(12)

        with self.canvas.before:
            Color(*self.original_background_color)
            self.rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[self.border_radius]
            )
        
        self.bind(size=self.update_rect, pos=self.update_rect)
        Window.bind(on_resize=self.on_window_resize)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.rect.radius = [self.border_radius]

    def on_window_resize(self, instance, width, height):
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.height = ResponsiveHelper.get_button_height()


# ------------------ NAVBAR RESPONSIVE ------------------
class NavbarAuth(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, 1)
        self.spacing = dp(10)
        
        self.update_dimensions()
        
        with self.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_rect, pos=self.update_rect)
        Window.bind(on_resize=self.on_window_resize)
        
        self.build_navbar()

    def build_navbar(self):
        self.clear_widgets()
        
        # Logo
        logo_height = ResponsiveHelper.get_logo_height()
        self.logo = Image(
            source="Imagen5-Photoroom.png",
            size_hint=(1, None),
            height=logo_height,
            fit_mode="contain"
        )
        self.add_widget(self.logo)

        # Espaciador después del logo
        spacer_height = dp(50) if Window.width >= 900 else dp(30)
        self.add_widget(Widget(size_hint_y=None, height=spacer_height))

        # Contenedor de botones
        self.botones_navbar = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )
        self.botones_navbar.bind(minimum_height=self.botones_navbar.setter('height'))
        self.agregar_botones()
        self.add_widget(self.botones_navbar)

        # Espaciador flexible
        self.add_widget(Widget(size_hint_y=1))

    def update_dimensions(self):
        self.width = ResponsiveHelper.get_navbar_width()
        padding_size = dp(20) if Window.width >= 600 else dp(10)
        self.padding = [padding_size, padding_size]

    def agregar_botones(self):
        menu_items = [
            ("Torneos", self.ir_a_torneos),
            ("Combates", self.ir_a_visualizar_combate),
            ("Crear Torneo", self.ir_a_crear_torneo),
            ("Crear Combate", self.ir_a_crear_combate),
            ("Mi cuenta", self.ir_a_cuenta),
            ("Cerrar Sesión", self.mostrar_popup_confirmacion)
        ]

        show_text = ResponsiveHelper.should_show_text()

        for text, action in menu_items:
            bg_color = (0.7, 0.1, 0.1, 1) if text == "Cerrar Sesión" else (0.1, 0.4, 0.7, 1)
            
            # En pantallas pequeñas, usar versiones cortas o iconos
            if not show_text:
                if text == "Crear Torneo":
                    text = "C.T."
                elif text == "Crear Combate":
                    text = "C.C."
                elif text == "Mi cuenta":
                    text = "Cuenta"
                elif text == "Cerrar Sesión":
                    text = "Salir"
            
            boton = HoverButton(text=text, bg_color=bg_color)
            boton.bind(on_press=action)
            self.botones_navbar.add_widget(boton)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.rebuild_navbar(), 0.1)

    def rebuild_navbar(self):
        self.update_dimensions()
        self.build_navbar()

    def ir_a_torneos(self, instance):
        App.get_running_app().root.current = 'torneos_anteriores'
    
    def ir_a_cuenta(self, instance):
        # Cambiar a la pantalla de perfil/cuenta
        app = App.get_running_app()
        
        # Si la pantalla de cuenta no existe, agregarla
        if not app.root.has_screen('cuenta'):
            try:
                app.root.add_widget(VerInfoScreen(name='cuenta'))
            except ImportError:
                print("[NavbarAuth] Error: Módulo ver_info no encontrado")
                return
        
        app.root.current = 'cuenta'

    def ir_a_crear_torneo(self, instance):
        App.get_running_app().root.current = 'crear_torneo'

    def ir_a_crear_combate(self, instance):
        App.get_running_app().root.current = 'crear_combate'

    def ir_a_visualizar_combate(self, instance):
        app = App.get_running_app()
        if not app.root.has_screen('combates_anteriores'):
            try:
                from combates_anteriore import CombatesScreen
                app.root.add_widget(CombatesScreen(name='combates_anteriores'))
            except ImportError:
                print("Módulo combates_anteriore no encontrado")
                return
        app.root.current = 'combates_anteriores'

    def mostrar_popup_confirmacion(self, instance):
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20)
        )

        lbl_mensaje = Label(
            text='¿Estás seguro que deseas\ncerrar sesión?',
            color=(0.5, 0.8, 1, 1),
            font_size=ResponsiveHelper.get_font_size(20),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(lbl_mensaje)

        btn_layout = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=ResponsiveHelper.get_button_height()
        )

        btn_cancelar = Button(
            text='CANCELAR',
            background_normal='',
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(16)
        )

        btn_confirmar = Button(
            text='CONFIRMAR',
            background_normal='',
            background_color=(0.7, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(16)
        )

        btn_layout.add_widget(btn_cancelar)
        btn_layout.add_widget(btn_confirmar)
        content.add_widget(btn_layout)

        popup_size = ResponsiveHelper.get_popup_size()
        self.popup = Popup(
            title='Confirmar acción',
            title_color=(1, 1, 1, 1),
            title_size=ResponsiveHelper.get_font_size(22),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=popup_size,
            separator_height=0,
            background=''
        )

        with self.popup.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.popup.rect = RoundedRectangle(
                pos=self.popup.pos,
                size=self.popup.size,
                radius=[dp(15)]
            )

        def update_popup_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

        self.popup.bind(pos=update_popup_rect, size=update_popup_rect)

        btn_cancelar.bind(on_press=self.popup.dismiss)
        btn_confirmar.bind(on_press=self.cerrar_sesion)

        self.popup.open()

    def cerrar_sesion(self, instance):
        """Cierra la sesión del administrador"""
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()
        
        try:
            # Intentar hacer logout en el backend
            api.admin_logout()
            print("[NavbarAuth] Logout exitoso en backend")
        except Exception as e:
            print(f"[NavbarAuth] Error al cerrar sesión en backend: {e}")
        finally:
            # Limpiar sesión local SIEMPRE (incluso si falla el backend)
            session.clear_session()
            api.clear_token()
            
            # Limpiar app.auth si existe
            app = App.get_running_app()
            if hasattr(app, 'auth'):
                app.auth = None
            
            print("[NavbarAuth] Sesión limpiada localmente")
            
            # Redirigir a la pantalla de inicio de sesión
            Clock.schedule_once(lambda dt: self._navegar_a_login(), 0.5)
    
    def _navegar_a_login(self):
        """Navega a la pantalla de inicio de sesión"""
        app = App.get_running_app()
        
        # Intentar encontrar la pantalla de inicio de sesión
        login_screen_names = ['inicio_sesion', 'login', 'main']
        
        for screen_name in login_screen_names:
            if app.root.has_screen(screen_name):
                app.root.current = screen_name
                print(f"[NavbarAuth] Navegando a pantalla: {screen_name}")
                return
        
        # Si no encuentra ninguna pantalla de login, intentar con el nombre por defecto
        if hasattr(app, 'LOGIN_SCREEN_NAME'):
            app.root.current = app.LOGIN_SCREEN_NAME
            print(f"[NavbarAuth] Navegando a pantalla por defecto: {app.LOGIN_SCREEN_NAME}")


# ------------------ PANTALLA PRINCIPAL RESPONSIVE ------------------
class MainInAuthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

    def on_pre_enter(self):
        """Verifica la sesión antes de entrar a la pantalla"""
        app = App.get_running_app()
        
        # Si no hay sesión en SessionManager, intentar recuperarla de app.auth
        if not session.is_logged_in() and hasattr(app, 'auth') and app.auth:
            session.set_session_from_app(app)
        
        # Si aún no hay sesión, redirigir al login
        if not session.is_logged_in():
            print("[MainInAuthScreen] No hay sesión activa, redirigiendo a login")
            Clock.schedule_once(lambda dt: self._ir_a_login(), 0.1)
    
    def _ir_a_login(self):
        """Navega a la pantalla de login"""
        app = App.get_running_app()
        login_screen_names = ['inicio_sesion', 'login', 'main']
        
        for screen_name in login_screen_names:
            if app.root.has_screen(screen_name):
                app.root.current = screen_name
                return
        
        if hasattr(app, 'LOGIN_SCREEN_NAME'):
            app.root.current = app.LOGIN_SCREEN_NAME

    def build_ui(self):
        self.clear_widgets()
        
        # Layout principal horizontal
        self.main_layout = BoxLayout(
            orientation='horizontal',
            spacing=0,
            padding=0
        )

        # Navbar
        self.navbar = NavbarAuth()
        self.main_layout.add_widget(self.navbar)

        # Contenedor principal del contenido (sin ScrollView aún)
        content_wrapper = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1)
        )

        # Fondo blanco para todo el contenedor
        with content_wrapper.canvas.before:
            Color(1, 1, 1, 1)
            self.wrapper_bg = Rectangle(
                size=content_wrapper.size,
                pos=content_wrapper.pos
            )
        
        # Función local para actualizar el fondo
        def update_wrapper_bg(instance, value):
            self.wrapper_bg.pos = instance.pos
            self.wrapper_bg.size = instance.size
        
        content_wrapper.bind(
            size=update_wrapper_bg,
            pos=update_wrapper_bg
        )

        # Contenedor de contenido con ScrollView
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=dp(10),
            bar_color=[0.1, 0.4, 0.7, 1],
            bar_inactive_color=[0.1, 0.4, 0.7, 0.5]
        )

        self.content_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=0
        )
        
        # Función para asegurar que el contenedor sea al menos tan alto como la ventana
        def update_min_height(instance, value):
            min_height = max(Window.height, self.content_layout.height)
            self.content_container.height = min_height
        
        self.content_container.bind(minimum_height=self.content_container.setter('height'))
        
        # Fondo blanco también en el content_container
        with self.content_container.canvas.before:
            Color(1, 1, 1, 1)
            self.content_bg = Rectangle(
                size=self.content_container.size,
                pos=self.content_container.pos
            )
        
        # Función local para actualizar el fondo del contenido
        def update_content_bg(instance, value):
            self.content_bg.pos = instance.pos
            self.content_bg.size = instance.size
        
        self.content_container.bind(
            size=update_content_bg,
            pos=update_content_bg
        )

        # Contenido principal
        padding_h = max(dp(30), Window.width * 0.05)
        padding_v = max(dp(20), Window.height * 0.03)
        
        self.content_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[padding_h, padding_v, padding_h, padding_v],
            size_hint_y=None
        )
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        # Espaciador superior
        top_spacer = max(dp(20), Window.height * 0.05)
        self.content_layout.add_widget(Widget(size_hint_y=None, height=top_spacer))

        # Título
        self.titulo = Label(
            text='PETO TECH',
            font_size=ResponsiveHelper.get_font_size(40),
            color=(0.1, 0.1, 0.2, 1),
            bold=True,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(80)
        )
        self.content_layout.add_widget(self.titulo)

        # Eslogan
        self.eslogan = Label(
            text='Bienvenido al sistema de gestión de torneos',
            font_size=ResponsiveHelper.get_font_size(24),
            color=(0.1, 0.4, 0.7, 1),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(60)
        )
        self.content_layout.add_widget(self.eslogan)

        # Espaciador
        self.content_layout.add_widget(Widget(size_hint_y=None, height=dp(30)))

        # Contenedor de imágenes responsive
        self.imagenes_layout = BoxLayout(
            orientation='horizontal' if Window.width > 600 else 'vertical',
            size_hint_y=None,
            spacing=dp(20)
        )
        
        # Altura responsive para las imágenes
        img_height = self.calculate_image_height()
        self.imagenes_layout.height = img_height

        self.img1 = Image(
            source="p1-Photoroom.png",
            size_hint_x=1 if Window.width > 600 else None,
            size_hint_y=None,
            height=img_height if Window.width <= 600 else img_height,
            width=Window.width * 0.8 if Window.width <= 600 else 0,
            fit_mode="contain"
        )
        
        self.img2 = Image(
            source="p2-Photoroom.png",
            size_hint_x=1 if Window.width > 600 else None,
            size_hint_y=None,
            height=img_height if Window.width <= 600 else img_height,
            width=Window.width * 0.8 if Window.width <= 600 else 0,
            fit_mode="contain"
        )
        
        self.imagenes_layout.add_widget(self.img1)
        if Window.width <= 600:
            self.imagenes_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))
        self.imagenes_layout.add_widget(self.img2)
        
        self.content_layout.add_widget(self.imagenes_layout)

        # Espaciador flexible
        self.content_layout.add_widget(Widget(size_hint_y=None, height=dp(30)))

        # Copyright
        self.copyright = Label(
            text="Copyright © 2025 - PetoTech System",
            font_size=ResponsiveHelper.get_font_size(14),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(40),
            halign="center"
        )
        self.content_layout.add_widget(self.copyright)

        # Espaciador inferior
        self.content_layout.add_widget(Widget(size_hint_y=None, height=dp(30)))

        self.content_container.add_widget(self.content_layout)
        scroll_view.add_widget(self.content_container)
        content_wrapper.add_widget(scroll_view)
        self.main_layout.add_widget(content_wrapper)
        self.add_widget(self.main_layout)

    def calculate_image_height(self):
        """Calcula altura apropiada para imágenes según tamaño de ventana"""
        if Window.width < 600:
            return dp(200)
        elif Window.width < 900:
            return dp(220)
        elif Window.width < 1200:
            return min(dp(250), Window.height * 0.3)
        else:
            return min(dp(300), Window.height * 0.35)

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)


# ------------------ APP PRINCIPAL ------------------
class MainApp(App):
    def build(self):
        from kivy.uix.screenmanager import ScreenManager
        sm = ScreenManager()
        sm.add_widget(MainInAuthScreen(name='main_auth'))
        return sm

    LOGIN_SCREEN_NAME = 'inicio_sesion'  # Cambiado de 'main' a 'inicio_sesion'
    auth = None

    def logout(self, call_backend=True):
        """
        Método de logout compatible con el código existente
        NOTA: Este método está deprecado, se recomienda usar session.clear_session()
        """
        try:
            if call_backend:
                try:
                    api.admin_logout()
                    print("[MainApp.logout] Logout exitoso en backend")
                except Exception as e:
                    print(f"[MainApp.logout] Error en backend: {e}")
        finally:
            try:
                # Limpiar sesión
                session.clear_session()
                api.clear_token()
                self.auth = None
                print("[MainApp.logout] Sesión limpiada")
            except Exception as e:
                print(f"[MainApp.logout] Error al limpiar sesión: {e}")
            
            # Navegar al login
            if self.root.has_screen(self.LOGIN_SCREEN_NAME):
                self.root.current = self.LOGIN_SCREEN_NAME

if __name__ == '__main__':
    MainApp().run()