from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.utils import platform
import requests, json
from threading import Thread
from kivy.app import App
from kivy.clock import Clock
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
            return 0.5  # 50% en pantallas grandes
    
    @staticmethod
    def get_font_size(base_size):
        width = Window.width
        if width < 600:
            return sp(base_size * 0.7)
        elif width < 900:
            return sp(base_size * 0.85)
        return sp(base_size)
    
    @staticmethod
    def get_popup_size():
        """Retorna tamaño apropiado para popups"""
        width = Window.width
        height = Window.height
        if width < 600:
            return (width * 0.9, min(height * 0.4, dp(300)))
        else:
            return (min(width * 0.6, dp(450)), min(height * 0.35, dp(250)))


# ------------------ TEXT INPUT REDONDEADO RESPONSIVE ------------------
class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Configuración mejorada
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

        # Efectos gráficos
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
            # Estado activo - más brillante
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
            # Estado normal
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


# ------------------ ENLACE RECUPERAR ------------------
class EnlaceRecuperar(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.on_window_resize)
    
    def on_window_resize(self, instance, width, height):
        self.font_size = ResponsiveHelper.get_font_size(16)


# ------------------ PANTALLA INICIO SESIÓN RESPONSIVE ------------------
class InicioSesionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        self.popup_usuario = None
        self.popup_correo = None
        Window.bind(on_resize=self.on_window_resize)

    def build_ui(self):
        self.clear_widgets()
        
        # Layout principal con ScrollView
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=dp(10)
        )
        
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(30), dp(20), dp(30)],
            spacing=dp(15),
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))

        # Fondo blanco
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.background_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self.update_background, pos=self.update_background)

        # Espaciador superior responsive
        top_spacer_height = max(dp(20), Window.height * 0.05)
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
        logo_height = min(dp(150), Window.height * 0.2)
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
            text='INICIO DE SESIÓN',
            font_size=ResponsiveHelper.get_font_size(32),
            color=(0.1, 0.4, 0.7, 1),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        form_container.add_widget(titulo)

        # Espaciador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # Campos de entrada
        campos_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None
        )
        campos_layout.bind(minimum_height=campos_layout.setter('height'))

        # Campo correo
        correo_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None
        )
        correo_layout.bind(minimum_height=correo_layout.setter('height'))
        
        correo_label = Label(
            text='Correo electrónico',
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.1, 0.1, 0.2, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        correo_label.bind(size=correo_label.setter('text_size'))
        correo_layout.add_widget(correo_label)
        
        self.correo_input = RoundedTextInput(hint_text='usuario@ejemplo.com')
        correo_layout.add_widget(self.correo_input)
        campos_layout.add_widget(correo_layout)

        # Campo contraseña
        contraseña_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None
        )
        contraseña_layout.bind(minimum_height=contraseña_layout.setter('height'))
        
        contraseña_label = Label(
            text='Contraseña',
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.1, 0.1, 0.2, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        contraseña_label.bind(size=contraseña_label.setter('text_size'))
        contraseña_layout.add_widget(contraseña_label)
        
        self.contraseña_input = RoundedTextInput(hint_text='********', password=True)
        contraseña_layout.add_widget(self.contraseña_input)
        campos_layout.add_widget(contraseña_layout)

        form_container.add_widget(campos_layout)

        # Espaciador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(15)))

        # Botones responsive
        botones_layout = BoxLayout(
            orientation='horizontal' if Window.width > 600 else 'vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(50) if Window.width > 600 else dp(110)
        )

        btn_iniciar = HoverButton(text='INICIAR SESIÓN')
        btn_iniciar.bind(on_press=self.iniciar_sesion)
        botones_layout.add_widget(btn_iniciar)

        btn_volver = HoverButton(text='VOLVER')
        # Cambiar color del canvas
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

        # Espaciador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # Enlace recuperar contraseña
        """recuperar_label = EnlaceRecuperar(
            text='¿Olvidaste tu contraseña?',
            font_size=ResponsiveHelper.get_font_size(16),
            color=(0.1, 0.4, 0.7, 1),
            underline=True,
            size_hint_y=None,
            height=dp(40)
        )
        recuperar_label.bind(on_press=self.mostrar_popup_usuario)
        form_container.add_widget(recuperar_label)"""

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

    def on_enter(self, *args):
        Clock.schedule_once(self.establecer_foco, 0.1)

    def establecer_foco(self, dt):
        if hasattr(self, 'correo_input'):
            self.correo_input.focus = True

    def iniciar_sesion(self, instance):
        login = self.correo_input.text.strip()   
        password = self.contraseña_input.text.strip()
        
        if not login or not password:
            self.mostrar_mensaje("Error", "Ingresa usuario/correo y contraseña.")
            return
    
        def _task():
            try:
                resp = api.post_json("/api/auth/admin/login", {"login": login, "password": password})
                
                if resp.status_code == 200:
                    data = resp.json()
                    access_token = data.get("accessToken")
                    admin = data.get("admin")
                    
                    if not access_token:
                        raise Exception("Respuesta sin token")
                    
                    # Configurar el token en el API client
                    api.set_access_token(access_token)
                    
                    # Guardar en app.auth (tu método actual)
                    app = App.get_running_app()
                    app.auth = {"access_token": access_token, "admin": admin}
                    
                    # NUEVO: Guardar la contraseña del administrador
                    app.admin_password = password  # <--- AGREGAR ESTA LÍNEA
                    
                    # NUEVO: También guardar en SessionManager
                    from session_manager import session
                    session.set_session(
                        admin_id=admin.get('idAdministrador'),
                        admin_data=admin,
                        access_token=access_token
                    )
                    
                    def _ok(dt):
                        self.manager.current = 'ini'
                        self.mostrar_mensaje("Éxito", f"Bienvenido {admin.get('usuarioAdministrador')}")
                    
                    Clock.schedule_once(_ok, 0)
                    
                elif resp.status_code in (400, 401):
                    try:
                        msg = resp.json().get("message", "Credenciales inválidas")
                    except Exception:
                        msg = "Credenciales inválidas"
                    
                    def _err(dt):
                        self.mostrar_mensaje("Error", msg)
                    Clock.schedule_once(_err, 0)
                else:
                    def _err2(dt):
                        self.mostrar_mensaje("Error", f"Error del servidor ({resp.status_code}).")
                    Clock.schedule_once(_err2, 0)
                    
            except requests.exceptions.ConnectionError:
                msg = "No se pudo conectar con el servidor."
                Clock.schedule_once(lambda dt, m=msg: self.mostrar_mensaje("Error", m), 0)
            except requests.exceptions.Timeout:
                msg = "Tiempo de espera agotado."
                Clock.schedule_once(lambda dt, m=msg: self.mostrar_mensaje("Error", m), 0)
            except Exception as e:
                msg = f"Ocurrió un error: {e}"
                Clock.schedule_once(lambda dt, m=msg: self.mostrar_mensaje("Error", m), 0)
    
        if hasattr(self, "show_loading"): 
            self.show_loading("Verificando...")
        
        Thread(target=_task, daemon=True).start()

    def mostrar_mensaje(self, titulo, mensaje):
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20)
        )

        # --- CAMBIO DE COLOR AQUÍ ---
        lbl_mensaje = Label(
            text=mensaje,
            color=(0.1, 0.4, 0.7, 1), # Azul brillante para el texto del pop-up
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
            color=(1, 1, 1, 1), # Se mantiene blanco para el botón
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

    def mostrar_popup_usuario(self, instance):
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20)
        )
        
        # --- CAMBIO DE COLOR AQUÍ ---
        lbl_usuario = Label(
            text='Ingresa tu nombre de usuario:',
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.1, 0.4, 0.7, 1), # Azul brillante para el texto del pop-up
            size_hint_y=None,
            height=dp(40)
        )
        
        txt_usuario = TextInput(
            hint_text='Tu nombre de usuario',
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            font_size=ResponsiveHelper.get_font_size(16),
            padding=[dp(10), dp(10)]
        )
        
        btn_aceptar = Button(
            text='ACEPTAR',
            size_hint_y=None,
            height=dp(45),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1), # Se mantiene blanco para el botón
            bold=True,
            font_size=ResponsiveHelper.get_font_size(18)
        )

        content.add_widget(lbl_usuario)
        content.add_widget(txt_usuario)
        content.add_widget(btn_aceptar)

        popup_size = ResponsiveHelper.get_popup_size()
        self.popup_usuario = Popup(
            title='Recuperar Contraseña',
            title_color=(1, 1, 1, 1),
            title_size=ResponsiveHelper.get_font_size(22),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=popup_size,
            separator_height=0,
            background=''
        )
        
        with self.popup_usuario.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.popup_usuario.rect = RoundedRectangle(
                pos=self.popup_usuario.pos,
                size=self.popup_usuario.size,
                radius=[dp(15)]
            )
        
        self.popup_usuario.bind(pos=self._update_popup_rect, size=self._update_popup_rect)
        btn_aceptar.bind(on_press=lambda btn: self.mostrar_popup_correo(txt_usuario.text))
        self.popup_usuario.open()

    def mostrar_popup_correo(self, usuario):
        if self.popup_usuario:
            self.popup_usuario.dismiss()
        
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20)
        )
        
        popup_size = ResponsiveHelper.get_popup_size()
        text_width = popup_size[0] - dp(40)
        
        # --- CAMBIO DE COLOR AQUÍ ---
        lbl_correo_enviado = Label(
            text=f'Se ha enviado un correo a la cuenta asociada con el usuario: {usuario}',
            color=(0.1, 0.4, 0.7, 1), # Azul brillante para el texto del pop-up
            font_size=ResponsiveHelper.get_font_size(16),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(100),
            text_size=(text_width, None)
        )
        
        btn_cerrar = Button(
            text='CERRAR',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1), # Se mantiene blanco para el botón
            bold=True,
            font_size=ResponsiveHelper.get_font_size(18)
        )
        btn_cerrar.bind(on_press=self.cerrar_popup_correo)
        
        content.add_widget(lbl_correo_enviado)
        content.add_widget(btn_cerrar)

        self.popup_correo = Popup(
            title='Recuperar Contraseña',
            title_color=(1, 1, 1, 1),
            title_size=ResponsiveHelper.get_font_size(22),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=popup_size,
            separator_height=0,
            background=''
        )
        
        with self.popup_correo.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.popup_correo.rect = RoundedRectangle(
                pos=self.popup_correo.pos,
                size=self.popup_correo.size,
                radius=[dp(15)]
            )
        
        self.popup_correo.bind(pos=self._update_popup_rect, size=self._update_popup_rect)
        self.popup_correo.open()

    def cerrar_popup_correo(self, instance):
        if self.popup_correo:
            self.popup_correo.dismiss()

    def _update_popup_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def volver(self, instance):
        self.manager.current = 'main'
