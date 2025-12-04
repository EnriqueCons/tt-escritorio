from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
import requests, json
from threading import Thread

API_BASE_URL = "http://localhost:8080"

class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url.strip("/")
        self.session = requests.Session()

    def post_json(self, path, payload):
        url = f"{self.base_url}{path}"
        return self.session.post(
            url,
            data=json.dumps(payload),
            headers={"Content-Type":"application/json","Accept":"application/json"},
            timeout=10
        )
api = ApiClient(API_BASE_URL)

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
            return 0.7   # 70% en pantallas medianas
        else:
            return 0.6   # 60% en pantallas grandes
    
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
    def get_popup_size():
        """Retorna tamaño apropiado para popups"""
        width = Window.width
        height = Window.height
        if width < 600:
            return (width * 0.9, min(height * 0.5, dp(400)))
        else:
            return (min(width * 0.7, dp(500)), min(height * 0.5, dp(400)))
    
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
    def get_button_layout_orientation():
        """Retorna orientación de botones según tamaño de ventana"""
        return 'horizontal' if Window.width > 600 else 'vertical'
    
    @staticmethod
    def get_button_layout_height():
        """Retorna altura del contenedor de botones"""
        return dp(50) if Window.width > 600 else dp(110)


# ------------------ TEXT INPUT REDONDEADO RESPONSIVE ------------------
class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_active = ""
        self.background_color = (0, 0, 0, 0)
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(55)
        self.padding = [dp(15), dp(15), dp(15), dp(15)]
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.color = (1, 1, 1, 1)
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
        # Extraer bg_color antes de llamar al constructor padre
        bg_color = kwargs.pop('bg_color', None)
        
        super().__init__(**kwargs)
        
        # Si no se pasó bg_color, usar el background_color actual o el default
        if bg_color is None:
            bg_color = self.background_color if hasattr(self, 'background_color') else (0.1, 0.4, 0.7, 1)
        
        self.background_normal = ''
        self.background_color = bg_color
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


# ------------------ PANTALLA REGISTRO RESPONSIVE ------------------
class RegistroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_popup = None
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

    def build_ui(self):
        self.clear_widgets()
        
        # Layout principal
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(10), dp(20), dp(10)],
            spacing=dp(10)
        )

        # Fondo gris claro
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.background_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self.update_background, pos=self.update_background)

        # Logo responsive centrado
        logo_height = ResponsiveHelper.get_logo_height()
        logo_container = BoxLayout(size_hint=(1, None), height=logo_height)
        logo = Image(
            source="Imagen5-Photoroom.png",
            size_hint=(None, None),
            width=logo_height * 1.2,
            height=logo_height,
            pos_hint={'center_x': 0.5},
            fit_mode="contain"
        )
        logo_container.add_widget(Widget())
        logo_container.add_widget(logo)
        logo_container.add_widget(Widget())
        main_layout.add_widget(logo_container)

        # ScrollView para el formulario
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=dp(10),
            scroll_type=['bars', 'content']
        )

        # Contenedor para centrar el formulario
        center_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None
        )
        center_container.bind(minimum_height=center_container.setter('height'))
        
        # Contenedor del formulario centrado y responsive
        form_container = BoxLayout(
            orientation='vertical',
            size_hint=(ResponsiveHelper.get_form_width(), None),
            spacing=dp(12),
            padding=[dp(20), dp(20)],
            pos_hint={'center_x': 0.5}
        )
        form_container.bind(minimum_height=form_container.setter('height'))

        # Título centrado
        titulo = Label(
            text='REGISTRO',
            font_size=ResponsiveHelper.get_font_size(32),
            color=(0.1, 0.4, 0.7, 1),
            bold=True,
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle'
        )
        form_container.add_widget(titulo)

        # Espaciador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # Función para crear campos de formulario
        def crear_campo(texto, hint_text, password=False):
            campo_layout = BoxLayout(
                orientation='vertical',
                spacing=dp(8),
                size_hint_y=None,
                size_hint_x=1
            )
            campo_layout.bind(minimum_height=campo_layout.setter('height'))

            label = Label(
                text=texto,
                font_size=ResponsiveHelper.get_font_size(18),
                color=(0.1, 0.1, 0.2, 1),
                size_hint_y=None,
                size_hint_x=1,
                height=dp(30),
                halign='center',
                valign='middle'
            )
            campo_layout.add_widget(label)

            input_field = RoundedTextInput(
                hint_text=hint_text,
                password=password,
                size_hint_y=None,
                size_hint_x=1,
                height=dp(55)
            )
            campo_layout.add_widget(input_field)

            return campo_layout, input_field

        # Campos del formulario
        campos = [
            ('Nombre', 'Ingresa tu nombre', False),
            ('Apellidos', 'Ingresa tus apellidos', False),
            ('Usuario', 'Ingresa tu usuario', False),
            ('Correo', 'usuario@ejemplo.com', False),
            ('Contraseña', '********', True),
            ('Confirmar Contraseña', '********', True)
        ]

        # Añadir campos al formulario
        for texto, hint, is_password in campos:
            layout, input_field = crear_campo(texto, hint, is_password)
            # Generar nombres de atributos consistentes
            attr_name = texto.lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u") + "_input"
            setattr(self, attr_name, input_field)
            form_container.add_widget(layout)

        # Espaciador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(15)))

        # Contenedor de botones responsive y centrado
        botones_layout = BoxLayout(
            orientation=ResponsiveHelper.get_button_layout_orientation(),
            spacing=dp(15),
            size_hint_y=None,
            size_hint_x=1,
            height=ResponsiveHelper.get_button_layout_height()
        )

        # Botón Registrar
        btn_registrar = HoverButton(
            text='REGISTRARSE',
            background_color=(0.1, 0.4, 0.7, 1),
            size_hint_x=1
        )
        btn_registrar.bind(on_press=self.registrar)
        botones_layout.add_widget(btn_registrar)

        # Botón Volver
        btn_volver = HoverButton(
            text='VOLVER',
            background_color=(0.7, 0.1, 0.1, 1),
            size_hint_x=1
        )
        # Actualizar canvas del botón volver
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

        # Espaciador final
        form_container.add_widget(Widget(size_hint_y=None, height=dp(20)))

        center_container.add_widget(form_container)
        scroll_view.add_widget(center_container)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

    def update_background(self, instance, value):
        self.background_rect.size = instance.size
        self.background_rect.pos = instance.pos

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)

    def on_enter(self, *args):
        Clock.schedule_once(self.establecer_foco, 0.1)

    def establecer_foco(self, dt):
        if hasattr(self, 'nombre_input'):
            self.nombre_input.focus = True

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
        btn_aceptar.bind(on_press=popup.dismiss)
        content.add_widget(btn_aceptar)
        popup.open()

    def show_loading(self, text="Creando cuenta..."):
        if self.loading_popup:
            return
        box = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        box.add_widget(Label(text=text, color=(1,1,1,1),
                             font_size=ResponsiveHelper.get_font_size(18)))
        self.loading_popup = Popup(title='',
                                   content=box,
                                   size_hint=(None,None),
                                   size=(dp(220), dp(120)),
                                   separator_height=0,
                                   background='')
        with self.loading_popup.canvas.before:
            Color(0,0,0,0.6)
            self.loading_rect = RoundedRectangle(pos=self.loading_popup.pos,
                                                 size=self.loading_popup.size,
                                                 radius=[dp(12)])
            
        def _upd(inst, val):
            self.loading_rect.pos = inst.pos
            self.loading_rect.size = inst.size
            self.loading_popup.bind(pos=_upd, size=_upd)
            self.loading_popup.open()

    def hide_loading(self):
        if self.loading_popup:
            self.loading_popup.dismiss()
            self.loading_popup = None

    def mostrar_popup_campos_faltantes_registro(self, campos_faltantes):
        scroll_content = ScrollView(size_hint=(1, 1))
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
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(35),
                halign='left'
            )
            label_campo.bind(size=label_campo.setter('text_size'))
            lista_campos.add_widget(label_campo)

        lista_campos.add_widget(Widget(size_hint_y=None, height=dp(10)))

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
        lista_campos.add_widget(btn_cerrar)

        scroll_content.add_widget(lista_campos)

        popup_size = ResponsiveHelper.get_popup_size()
        popup = Popup(
            title='¡Atención!',
            title_color=(1, 1, 1, 1),
            title_size=ResponsiveHelper.get_font_size(22),
            title_align='center',
            content=scroll_content,
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
        btn_cerrar.bind(on_press=popup.dismiss)
        popup.open()

    def registrar(self, instance):
        required_fields = [
            (self.nombre_input, "Por favor ingresa tu nombre"),
            (self.apellidos_input, "Por favor ingresa tus apellidos"),
            (self.usuario_input, "Por favor ingresa un nombre de usuario"),
            (self.correo_input, "Por favor ingresa tu correo electrónico"),
            (self.contraseña_input, "Por favor ingresa una contraseña")
        ]

        campos_faltantes = [msg for campo, msg in required_fields if not campo.text.strip()]
        if campos_faltantes:
            self.mostrar_popup_campos_faltantes_registro(campos_faltantes)
            return

        if "@" not in self.correo_input.text or "." not in self.correo_input.text:
            self.mostrar_mensaje("Correo inválido", "Por favor ingresa un correo electrónico válido")
            self.correo_input.focus = True
            return

        if self.contraseña_input.text != self.confirmar_contraseña_input.text:
            self.mostrar_mensaje("Error en contraseña", "Las contraseñas no coinciden")
            self.contraseña_input.text = ""
            self.confirmar_contraseña_input.text = ""
            self.contraseña_input.focus = True
            return

        if len(self.contraseña_input.text) < 8:
            self.mostrar_mensaje("Contraseña débil", "La contraseña debe tener al menos 8 caracteres")
            self.contraseña_input.text = ""
            self.confirmar_contraseña_input.text = ""
            self.contraseña_input.focus = True
            return

        # Mapear "Apellidos" en paterno/materno (si luego los separas, quita esta lógica)
        apellidos = self.apellidos_input.text.strip()
        partes = apellidos.split(" ", 1)
        paterno = partes[0]
        materno = partes[1] if len(partes) > 1 else ""

        payload = {
            "nombreAdministrador": self.nombre_input.text.strip(),
            "paternoAdministrador": paterno,
            "maternoAdministrador": materno,
            "usuarioAdministrador": self.usuario_input.text.strip(),
            "correoAdministrador": self.correo_input.text.strip(),
            "contraseniaAdministrador": self.contraseña_input.text
        }

        def _task():
            try:
                resp = api.post_json("/apiAdministradores/administrador", payload)
                if resp.status_code in (200, 201):
                    # Éxito
                    def _ok(dt):
                        self.hide_loading()
                        self.manager.current = 'main'
                        self.mostrar_mensaje(
                            "¡Registro exitoso!",
                            f"Bienvenido {self.nombre_input.text} {self.apellidos_input.text}"
                        )
                        # Limpiar campos
                        for campo in [self.nombre_input, self.apellidos_input, self.usuario_input,
                                    self.correo_input, self.contraseña_input, self.confirmar_contraseña_input]:
                            campo.text = ""
                        # (Opcional) Navegar a login si lo deseas
                        # self.manager.current = 'login'
                    Clock.schedule_once(_ok, 0)
                else:
                    try:
                        msg = resp.json().get("message", f"Error {resp.status_code}")
                    except Exception:
                        msg = f"Error {resp.status_code}"
                    def _err(dt):
                        self.hide_loading()
                        self.mostrar_mensaje("Error", msg)
                    Clock.schedule_once(_err, 0)

            except requests.exceptions.ConnectionError:
                def _net(dt):
                    self.hide_loading()
                    self.mostrar_mensaje("Error", "No se pudo conectar con el servidor.")
                Clock.schedule_once(_net, 0)
            except requests.exceptions.Timeout:
                def _to(dt):
                    self.hide_loading()
                    self.mostrar_mensaje("Error", "Tiempo de espera agotado.")
                Clock.schedule_once(_to, 0)
            except Exception as e:
                def _ex(dt):
                    self.hide_loading()
                    self.mostrar_mensaje("Error", f"Ocurrió un error: {str(e)}")
                Clock.schedule_once(_ex, 0)

        self.show_loading("Creando cuenta...")
        Thread(target=_task, daemon=True).start()

    def volver(self, instance):
        self.manager.current = 'main'


# ------------------ APP DE PRUEBA ------------------
class RegistroApp(App):
    def build(self):
        from kivy.uix.screenmanager import ScreenManager
        sm = ScreenManager()
        sm.add_widget(RegistroScreen(name='registro'))
        return sm


if __name__ == '__main__':
    RegistroApp().run()