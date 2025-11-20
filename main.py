from kivy.config import Config

# ⭐ Configurar tamaño ANTES de importar cualquier cosa de Kivy
Config.set('graphics', 'width', '1600')
Config.set('graphics', 'height', '900')
Config.set('graphics', 'resizable', True)
Config.set('graphics', 'minimum_width', '1200')
Config.set('graphics', 'minimum_height', '700')

# Posicionar ventana (opcional)
Config.set('graphics', 'position', 'auto')

# NO escribir archivo config (evita conflictos)
Config.set('kivy', 'exit_on_escape', '1')


from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.clock import Clock
import webbrowser
import os

# Importaciones de tus pantallas
from registro import RegistroScreen
from torneos_anteriores import TorneosAnterioresScreen
from crear_torneo import CrearTorneoScreen
from crear_combate import CrearCombateScreen
from tablero import MainScreentab
from tablero_central import MainScreentabc
from combates_anteriore import CombatesScreen
from inicio import InicioSesionScreen
from ini import MainInAuthScreen
from ini_juez import InicioSesionJuezScreen
from cuenta import VerInfoScreen
from actualizar_torneos import ActualizarTorneoScreen
from actualizar import ActualizarDatosScreen
from api_client import api

# ------------------ UTILIDADES MULTIPLATAFORMA ------------------
class ResponsiveHelper:
    """Clase helper para manejar dimensiones responsive"""
    
    @staticmethod
    def get_window_width():
        return Window.width
    
    @staticmethod
    def get_window_height():
        return Window.height
    
    @staticmethod
    def is_mobile():
        return platform in ['android', 'ios']
    
    @staticmethod
    def is_desktop():
        return platform in ['win', 'linux', 'macosx']
    
    @staticmethod
    def get_navbar_width():
        """Retorna el ancho apropiado para la navbar según el dispositivo"""
        width = Window.width
        if ResponsiveHelper.is_mobile() or width < 800:
            return 0.25  # 25% en móviles o ventanas pequeñas
        elif width < 1200:
            return 0.22  # 22% en ventanas medianas
        elif width < 1600:
            return 0.20  # 20% en ventanas grandes
        else:
            return 0.18  # 18% en ventanas muy grandes
    
    @staticmethod
    def get_font_size(base_size):
        """Ajusta el tamaño de fuente según la resolución"""
        width = Window.width
        height = Window.height
        min_dimension = min(width, height)
        
        # ⭐ MEJORADO: Escala mejor para pantallas grandes
        if ResponsiveHelper.is_mobile() or width < 800:
            return sp(base_size * 0.75)
        elif width < 1200:
            return sp(base_size * 0.90)
        elif width < 1600:
            return sp(base_size * 1.0)   # Tamaño normal
        elif width < 1920:
            return sp(base_size * 1.15)  
        else:
            return sp(base_size * 1.3)  
    
    @staticmethod
    def get_spacing():
        """Retorna espaciado apropiado"""
        width = Window.width
        if width < 800:
            return dp(8)
        elif width < 1200:
            return dp(10)
        elif width < 1600:
            return dp(12)
        else:
            return dp(15) 
    
    @staticmethod
    def get_padding():
        """Retorna padding apropiado"""
        width = Window.width
        if ResponsiveHelper.is_mobile() or width < 800:
            return [dp(10), dp(10)]
        elif width < 1200:
            return [dp(20), dp(20)]
        elif width < 1600:
            return [dp(25), dp(25)]
        else:
            return [dp(30), dp(30)]  # ⭐ Mayor padding en pantallas grandes
    
    @staticmethod
    def get_popup_size():
        """Retorna tamaño apropiado para popups"""
        width = Window.width
        height = Window.height
        
        if width < 600:
            return (width * 0.9, min(height * 0.4, dp(300)))
        elif width < 1200:
            return (min(width * 0.6, dp(450)), min(height * 0.35, dp(250)))
        elif width < 1600:
            return (min(width * 0.5, dp(600)), min(height * 0.4, dp(350)))
        else:
            return (min(width * 0.4, dp(800)), min(height * 0.4, dp(450)))  # ⭐ Popups más grandes
    
    @staticmethod
    def get_layout_orientation():
        """Determina si el layout debe ser horizontal o vertical"""
        return 'horizontal' if Window.width > Window.height and Window.width > 800 else 'vertical'
    
    @staticmethod
    def get_button_height():
        """Retorna altura de botones responsive"""
        width = Window.width
        if width < 600:
            return dp(40)
        elif width < 1200:
            return dp(50)
        elif width < 1600:
            return dp(55)
        else:
            return dp(60) 
    
    @staticmethod
    def get_score_font_size():
        """⭐ Tamaño especial para números de puntaje (más grandes)"""
        width = Window.width
        if width < 800:
            return sp(40)
        elif width < 1200:
            return sp(50)
        elif width < 1600:
            return sp(70)
        elif width < 1920:
            return sp(90)   # ⭐ Muy grande para Full HD
        else:
            return sp(120)  # ⭐ Extra grande para 4K
    
    @staticmethod
    def get_form_width():
        """Retorna ancho del formulario según pantalla"""
        width = Window.width
        if width < 600:
            return 0.95
        elif width < 900:
            return 0.85
        elif width < 1200:
            return 0.75
        elif width < 1600:
            return 0.65
        else:
            return 0.55  # ⭐ Más estrecho en pantallas grandes (mejor legibilidad)
# ------------------ BOTÓN CON EFECTO HOVER RESPONSIVE ------------------
class HoverButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_background_color = (0.1, 0.4, 0.7, 1)
        self.hover_background_color = (0.2, 0.5, 0.9, 1)
        self.background_color = self.original_background_color
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = ResponsiveHelper.get_font_size(16)
        self.color = (1, 1, 1, 1)
        self.border_radius = dp(25)
        self.background_normal = ''
        self.background_down = ''

        with self.canvas.before:
            Color(*self.original_background_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.border_radius])
        self.bind(size=self.update_rect, pos=self.update_rect)
        
        # Actualizar tamaño de fuente cuando cambie la ventana
        Window.bind(on_resize=self.on_window_resize)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.rect.radius = [self.border_radius]
    
    def on_window_resize(self, instance, width, height):
        self.font_size = ResponsiveHelper.get_font_size(16)
        self.height = dp(50)


# ------------------ NAVBAR RESPONSIVE ------------------
class Navbar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (ResponsiveHelper.get_navbar_width(), 1)
        self.orientation = "vertical"
        self.padding = ResponsiveHelper.get_padding()
        self.spacing = ResponsiveHelper.get_spacing()

        with self.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        # ScrollView para navbar en caso de overflow
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, bar_width=0)
        scroll_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        scroll_content.bind(minimum_height=scroll_content.setter('height'))

        # Logo responsive
        self.logo = Image(
            source="Imagen5-Photoroom.png", 
            size_hint=(1, None), 
            height=dp(120),
            allow_stretch=True,
            keep_ratio=True
        )
        scroll_content.add_widget(self.logo)

        # Espaciador
        scroll_content.add_widget(Widget(size_hint_y=None, height=dp(10)))

        menu_items = [
            ("Manual de usuario", self.descargar_manual),
            ("Contáctanos", self.enviar_correo),
            ("Conócenos", self.ir_a_conocenos),
        ]

        for text, action in menu_items:
            boton = HoverButton(text=text)
            boton.bind(on_press=action)
            scroll_content.add_widget(boton)

        scroll.add_widget(scroll_content)
        self.add_widget(scroll)
        
        # Actualizar cuando cambie el tamaño de ventana
        Window.bind(on_resize=self.on_window_resize)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
    
    def on_window_resize(self, instance, width, height):
        self.size_hint = (ResponsiveHelper.get_navbar_width(), 1)
        self.logo.height = dp(120)
        self.spacing = ResponsiveHelper.get_spacing()
        self.padding = ResponsiveHelper.get_padding()

    def descargar_manual(self, instance):
        # Manejo multiplataforma de rutas
        manual_path = "ilovepdf_merged (2)[1].pdf"
        if os.path.exists(manual_path):
            if platform == 'win':
                os.startfile(manual_path)
            elif platform == 'macosx':
                os.system(f'open "{manual_path}"')
            else:  # linux
                os.system(f'xdg-open "{manual_path}"')
        else:
            webbrowser.open(manual_path)

    def enviar_correo(self, instance):
        webbrowser.open("mailto:karlycid0925@gmail.com")

    def ir_a_conocenos(self, instance):
        App.get_running_app().root.current = 'conocenos'


# ------------------ LABEL RESPONSIVE ------------------
class ResponsiveLabel(Label):
    """Label que ajusta automáticamente su altura según el contenido"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.bind(texture_size=self.on_texture_size)
        # Programar actualización de text_size después de que se renderice
        Clock.schedule_once(self.update_text_size, 0)
    
    def update_text_size(self, dt):
        if self.text_size[0] is None:
            self.text_size = (self.width, None)
    
    def on_texture_size(self, instance, value):
        self.height = value[1] + dp(20)
    
    def on_size(self, instance, value):
        if self.text_size[0] != self.width:
            self.text_size = (self.width, None)


# ------------------ PANTALLA CONÓCENOS RESPONSIVE ------------------
class ConocenosScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

    def build_ui(self):
        self.clear_widgets()
        
        main_layout = BoxLayout(
            orientation='horizontal', 
            spacing=0
        )
        self.navbar = Navbar()
        main_layout.add_widget(self.navbar)

        content_layout = BoxLayout(
            orientation='vertical', 
            spacing=0, 
            size_hint=(1 - ResponsiveHelper.get_navbar_width(), 1)
        )
        with content_layout.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self.background_rect = Rectangle(size=content_layout.size, pos=content_layout.pos)
        content_layout.bind(size=self.update_background_rect, pos=self.update_background_rect)

        scroll_view = ScrollView(
            size_hint=(1, 1), 
            do_scroll_x=False, 
            bar_width=dp(10),
            scroll_type=['bars', 'content'],
            bar_color=(0.5, 0.5, 0.5, 1),
            bar_inactive_color=(0.7, 0.7, 0.7, 0.5)
        )

        main_content = BoxLayout(
            orientation='vertical', 
            spacing=dp(20), 
            padding=[dp(15), dp(20), dp(15), dp(30)],
            size_hint_y=None
        )
        main_content.bind(minimum_height=main_content.setter('height'))
        
        # Fondo para el contenido del scroll
        with main_content.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self.main_content_rect = Rectangle(size=main_content.size, pos=main_content.pos)
        main_content.bind(size=self.update_main_content_rect, pos=self.update_main_content_rect)

        # Título
        titulo = ResponsiveLabel(
            text='[b]CONÓCENOS[/b]',
            font_size=ResponsiveHelper.get_font_size(36), 
            markup=True,
            color=(0.1, 0.3, 0.6, 1),
            halign='center',
            size_hint_y=None,
            height=dp(80)
        )
        main_content.add_widget(titulo)

        # -------- Función para secciones --------
        def crear_seccion(titulo_seccion, contenido):
            box = BoxLayout(
                orientation='vertical', 
                size_hint_y=None,
                spacing=dp(8),
                padding=[dp(10), dp(10)]
            )
            box.bind(minimum_height=box.setter('height'))
            
            # Fondo con borde para cada sección
            with box.canvas.before:
                Color(1, 1, 1, 1)
                box.bg_rect = RoundedRectangle(size=box.size, pos=box.pos, radius=[dp(15)])
                Color(0.1, 0.4, 0.7, 0.3)
                box.border_rect = RoundedRectangle(
                    size=box.size, 
                    pos=box.pos, 
                    radius=[dp(15)]
                )
            
            def update_box_rects(instance, value):
                box.bg_rect.size = instance.size
                box.bg_rect.pos = instance.pos
                box.border_rect.size = instance.size
                box.border_rect.pos = instance.pos
            
            box.bind(size=update_box_rects, pos=update_box_rects)
            
            lbl_titulo = ResponsiveLabel(
                text=f"[b]{titulo_seccion}[/b]", 
                markup=True,
                font_size=ResponsiveHelper.get_font_size(22), 
                color=(0.1, 0.4, 0.7, 1),
                halign='center'
            )
            
            lbl_contenido = ResponsiveLabel(
                text=contenido,
                font_size=ResponsiveHelper.get_font_size(16), 
                color=(0.2, 0.2, 0.2, 1),
                halign='center',
                valign='top'
            )
            
            box.add_widget(lbl_titulo)
            box.add_widget(lbl_contenido)
            return box

        # Contenedor para Misión y Visión lado a lado
        mision_vision_container = BoxLayout(
            orientation='horizontal' if Window.width > 800 else 'vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=[dp(10), 0]
        )
        mision_vision_container.bind(minimum_height=mision_vision_container.setter('height'))
        
        seccion_mision = crear_seccion(
            "MISIÓN",
            "En Peto Tech desarrollamos soluciones tecnológicas innovadoras para la gestión de torneos deportivos, "
            "facilitando la organización, seguimiento y análisis de combates mediante herramientas intuitivas."
        )
        
        seccion_vision = crear_seccion(
            "VISIÓN",
            "Ser líderes en software deportivo, destacando por nuestra innovación, calidad y compromiso con los usuarios."
        )
        
        mision_vision_container.add_widget(seccion_mision)
        mision_vision_container.add_widget(seccion_vision)
        main_content.add_widget(mision_vision_container)

        # -------- Galería Responsive --------
        gallery_title = ResponsiveLabel(
            text="[b]CONOCE A NUESTRO EQUIPO[/b]",
            markup=True, 
            font_size=ResponsiveHelper.get_font_size(22),
            color=(0.1, 0.3, 0.6, 1),
            halign='center',
            size_hint_y=None,
            height=dp(60)
        )
        main_content.add_widget(gallery_title)

        # Contenedor centrado para las tarjetas
        gallery_container = AnchorLayout(
            anchor_x='center',
            anchor_y='top',
            size_hint_y=None,
            height=dp(300)
        )
        
        # Contenedor de galería con scroll horizontal
        gallery_scroll = ScrollView(
            size_hint=(None, None),
            size=(min(Window.width * 0.9, dp(600)), dp(280)),
            do_scroll_y=False,
            bar_width=dp(10)
        )
        
        img_grid = BoxLayout(
            orientation='horizontal', 
            spacing=dp(15), 
            size_hint=(None, 1),
            padding=[dp(10), 0]
        )
        img_grid.bind(minimum_width=img_grid.setter('width'))

        class TeamCard(BoxLayout):
            def __init__(self, image_path, name, role, **kwargs):
                super().__init__(
                    orientation='vertical', 
                    size_hint=(None, None),
                    size=(dp(180), dp(240)), 
                    padding=dp(10), 
                    spacing=dp(5), 
                    **kwargs
                )
                with self.canvas.before:
                    Color(0.9, 0.9, 0.9, 1)
                    self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
                self.bind(
                    size=lambda c, v: setattr(c.rect, 'size', v),
                    pos=lambda c, v: setattr(c.rect, 'pos', v)
                )
                
                img = Image(
                    source=image_path, 
                    size_hint_y=0.65, 
                    allow_stretch=True,
                    keep_ratio=True
                )
                self.add_widget(img)
                
                self.add_widget(Label(
                    text=f"[b]{name}[/b]", 
                    markup=True, 
                    color=(0.1, 0.4, 0.7, 1),
                    font_size=ResponsiveHelper.get_font_size(16),
                    size_hint_y=0.2
                ))
                self.add_widget(Label(
                    text=role, 
                    color=(0.4, 0.4, 0.4, 1),
                    font_size=ResponsiveHelper.get_font_size(14),
                    size_hint_y=0.15
                ))

        img_grid.add_widget(TeamCard("p1-Photoroom.png", "Karla", "Desarrolladora"))
        img_grid.add_widget(TeamCard("p2-Photoroom.png", "Enrique", "Diseñador UI/UX"))
        img_grid.add_widget(TeamCard("p2-Photoroom.png", "Leonardo", "Backend Developer"))

        gallery_scroll.add_widget(img_grid)
        gallery_container.add_widget(gallery_scroll)
        main_content.add_widget(gallery_container)

        # Espaciador
        main_content.add_widget(Widget(size_hint_y=None, height=dp(20)))

        # Botón volver
        btn_back = HoverButton(
            text="Volver al Inicio", 
            size_hint=(None, None), 
            size=(dp(300), dp(50))
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        
        btn_container = AnchorLayout(
            anchor_x='center', 
            anchor_y='top',
            size_hint_y=None, 
            height=dp(70)
        )
        btn_container.add_widget(btn_back)
        main_content.add_widget(btn_container)

        scroll_view.add_widget(main_content)
        content_layout.add_widget(scroll_view)
        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)

    def update_background_rect(self, instance, value):
        self.background_rect.size = instance.size
        self.background_rect.pos = instance.pos
    
    def update_main_content_rect(self, instance, value):
        """Actualiza el fondo del contenido del scroll"""
        self.main_content_rect.size = instance.size
        self.main_content_rect.pos = instance.pos
    
    def on_window_resize(self, instance, width, height):
        # Reconstruir UI al cambiar tamaño
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)


# ------------------ PANTALLA PRINCIPAL RESPONSIVE ------------------
class MainInScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

    def build_ui(self):
        self.clear_widgets()
        
        main_layout = BoxLayout(
            orientation='horizontal', 
            spacing=0
        )
        self.navbar = Navbar()
        main_layout.add_widget(self.navbar)

        # ScrollView para contenido principal
        scroll_view = ScrollView(
            size_hint=(1 - ResponsiveHelper.get_navbar_width(), 1),
            do_scroll_x=False,
            bar_width=dp(10),
            bar_color=(0.5, 0.5, 0.5, 1),
            bar_inactive_color=(0.7, 0.7, 0.7, 0.5)
        )

        content_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(15), 
            padding=ResponsiveHelper.get_padding(),
            size_hint_y=None
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        with content_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.background_rect = Rectangle(size=content_layout.size, pos=content_layout.pos)
        content_layout.bind(size=self.update_background_rect, pos=self.update_background_rect)

        # Espaciador superior
        content_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))

        titulo = ResponsiveLabel(
            text='PETO TECH',
            font_size=ResponsiveHelper.get_font_size(60), 
            bold=True,
            color=(0.1, 0.1, 0.2, 1),
            halign="center",
            size_hint_y=None,
            height=dp(80)
        )
        
        eslogan = ResponsiveLabel(
            text='Tu solución tecnológica para la gestión de torneos de Taekwondo.',
            font_size=ResponsiveHelper.get_font_size(20), 
            color=(0.1, 0.4, 0.7),
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )

        botones = BoxLayout(
            spacing=dp(15), 
            size_hint=(1, None), 
            height=dp(50),
            padding=[dp(20), 0]
        )
        btn_login = HoverButton(text="INICIAR SESIÓN")
        btn_login.bind(on_press=lambda x: setattr(self.manager, 'current', 'inicio_sesion'))
        btn_reg = HoverButton(text="REGISTRARSE")
        btn_reg.bind(on_press=lambda x: setattr(self.manager, 'current', 'registro'))
        botones.add_widget(btn_login)
        botones.add_widget(btn_reg)

        btn_juez = HoverButton(
            text="ACCESO JUEZ", 
            size_hint=(None, None), 
            size=(min(dp(400), Window.width * 0.5), dp(45))
        )
        btn_juez.bind(on_press=lambda x: setattr(App.get_running_app().root, 'current', 'ini_juez'))
        
        btn_juez_container = AnchorLayout(
            anchor_x='center',
            size_hint_y=None, 
            height=dp(60)
        )
        btn_juez_container.add_widget(btn_juez)

        quienes = ResponsiveLabel(
            text="Somos un equipo dedicado a ofrecer soluciones tecnológicas innovadoras para el deporte.",
            font_size=ResponsiveHelper.get_font_size(16), 
            color=(0.1, 0.1, 0.1, 1),
            halign="center"
        )

        imagenes = BoxLayout(
            orientation="horizontal", 
            spacing=dp(15), 
            size_hint=(1, None), 
            height=dp(250),
            padding=[dp(20), 0]
        )
        imagenes.add_widget(Image(
            source="p1-Photoroom.png",
            allow_stretch=True,
            keep_ratio=True
        ))
        imagenes.add_widget(Image(
            source="p2-Photoroom.png",
            allow_stretch=True,
            keep_ratio=True
        ))

        footer = Label(
            text="© 2025 - PetoTech System", 
            font_size=ResponsiveHelper.get_font_size(14), 
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(40)
        )

        content_layout.add_widget(titulo)
        content_layout.add_widget(eslogan)
        content_layout.add_widget(botones)
        content_layout.add_widget(btn_juez_container)
        content_layout.add_widget(quienes)
        content_layout.add_widget(imagenes)
        content_layout.add_widget(footer)
        
        # Espaciador inferior grande para cubrir todo el scroll
        content_layout.add_widget(Widget(size_hint_y=None, height=dp(50)))
        
        # Fondo extra que cubre todo el contenido del scroll
        with scroll_view.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.scroll_background = Rectangle(size=scroll_view.size, pos=scroll_view.pos)
        scroll_view.bind(size=self.update_scroll_background, pos=self.update_scroll_background)

        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

    def update_background_rect(self, instance, value):
        self.background_rect.size = instance.size
        self.background_rect.pos = instance.pos
    
    def update_scroll_background(self, instance, value):
        """Actualiza el fondo del ScrollView para evitar negro"""
        self.scroll_background.size = instance.size
        self.scroll_background.pos = instance.pos
    
    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)


# ------------------ APLICACIÓN ------------------
class MyApp(App):

    LOGIN_SCREEN_NAME = 'main'
    auth = None

    def build(self):
        # Configuración de ventana inicial multiplataforma
        if ResponsiveHelper.is_desktop():
            Window.size = (1280, 720)
            Window.minimum_width = 800
            Window.minimum_height = 600
        
        sm = ScreenManager()
        sm.add_widget(MainInScreen(name='main'))
        sm.add_widget(ConocenosScreen(name='conocenos'))
        sm.add_widget(InicioSesionScreen(name='inicio_sesion'))
        sm.add_widget(RegistroScreen(name='registro'))
        sm.add_widget(TorneosAnterioresScreen(name='torneos_anteriores'))
        sm.add_widget(CrearTorneoScreen(name='crear_torneo'))
        sm.add_widget(CrearCombateScreen(name='crear_combate'))
        sm.add_widget(MainScreentab(name='visualizar_combate'))
        sm.add_widget(MainScreentabc(name='visualizar_tablero_central'))
        sm.add_widget(MainInAuthScreen(name='ini'))
        sm.add_widget(InicioSesionJuezScreen(name='ini_juez'))
        sm.add_widget(VerInfoScreen(name='cuenta'))
        sm.add_widget(ActualizarDatosScreen(name='actualizar'))
        sm.add_widget(CombatesScreen(name='combates_anteriores'))
        # ActualizarTorneoScreen se agregará dinámicamente cuando se necesite
        return sm
    
    def agregar_pantalla_actualizar_torneo(self, torneo_data, on_save_callback):
        """
        Método para agregar dinámicamente la pantalla de actualizar torneo
        """
        sm = self.root
        
        # Remover pantalla anterior si existe
        if sm.has_screen('actualizar_torneos'):
            sm.remove_widget(sm.get_screen('actualizar_torneos'))
        
        # Crear y agregar nueva pantalla con los datos
        screen = ActualizarTorneoScreen(
            name='actualizar_torneos',
            torneo_data=torneo_data,
            on_save=on_save_callback
        )
        sm.add_widget(screen)
        sm.current = 'actualizar_torneos'

    def logout(self, call_backend=True):
        """
        Cierra sesión de forma segura:
        - Intenta informar al backend (si call_backend=True).
        - Limpia token local y estado de auth.
        - Navega a LOGIN_SCREEN_NAME.
        """
        try:
            if call_backend:
                try:
                    api.post_logout()  # no interrumpimos si falla
                except Exception:
                    pass
        finally:
            # borra token y estado local
            try:
                api.clear_token()
            except Exception:
                pass
            self.auth = None

            # Navega de vuelta a la pantalla de landing/login
            if self.root and self.root.has_screen(self.LOGIN_SCREEN_NAME):
                self.root.current = self.LOGIN_SCREEN_NAME
            elif self.root and getattr(self.root, 'screen_names', None):
                # fallback defensivo
                self.root.current = self.root.screen_names[0]


if __name__ == '__main__':
    MyApp().run()