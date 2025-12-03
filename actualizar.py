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
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
from threading import Thread
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
            return 0.6
    
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
        bg_color = kwargs.pop('background_color', (0.1, 0.4, 0.7, 1))
        
        super().__init__(**kwargs)
        
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
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.border_radius])

        self.bind(pos=self.update_rect, size=self.update_rect)
        Window.bind(on_resize=self.on_window_resize)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_window_resize(self, instance, width, height):
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.height = dp(50)


# ------------------ PANTALLA ACTUALIZAR DATOS ------------------
class ActualizarDatosScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.admin_data = None
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

    def on_pre_enter(self):
        """Se ejecuta antes de mostrar la pantalla"""
        self.cargar_datos_actuales()

    def cargar_datos_actuales(self):
        """Carga los datos actuales del administrador"""
        try:
            # Verificar sesión
            if not session.is_logged_in():
                self.mostrar_mensaje("Error", "No hay sesión activa.")
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'inicio_sesion'), 2)
                return
            
            admin_id = session.get_admin_id()
            print(f"[ActualizarDatosScreen] Cargando datos del admin ID: {admin_id}")
            
            # Obtener datos frescos del backend
            self.admin_data = api.get_administrador_by_id(admin_id)
            
            # Actualizar campos con los datos
            self.actualizar_campos_ui()
            
        except Exception as e:
            print(f"[ActualizarDatosScreen] Error al cargar datos: {e}")
            # Intentar usar datos en caché
            cached_data = session.get_admin_data()
            if cached_data:
                self.admin_data = cached_data
                self.actualizar_campos_ui()
            else:
                self.mostrar_mensaje("Error", f"No se pudieron cargar los datos: {str(e)}")

    def set_admin_data(self, admin_data):
        """Método para recibir datos desde otra pantalla"""
        self.admin_data = admin_data
        self.actualizar_campos_ui()

    def actualizar_campos_ui(self):
        """Actualiza los campos del formulario con los datos del administrador"""
        if not self.admin_data:
            return
        
        if hasattr(self, 'nombre_input'):
            self.nombre_input.text = self.admin_data.get('nombreAdministrador', '')
        
        if hasattr(self, 'paterno_input'):
            self.paterno_input.text = self.admin_data.get('paternoAdministrador', '')
        
        if hasattr(self, 'materno_input'):
            self.materno_input.text = self.admin_data.get('maternoAdministrador', '')
        
        if hasattr(self, 'usuario_input'):
            self.usuario_input.text = self.admin_data.get('usuarioAdministrador', '')
        
        if hasattr(self, 'correo_input'):
            self.correo_input.text = self.admin_data.get('correoAdministrador', '')
        
        # La contraseña siempre empieza vacía
        if hasattr(self, 'nueva_contraseña_input'):
            self.nueva_contraseña_input.text = ''

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

        # Título
        titulo = Label(
            text='ACTUALIZAR DATOS',
            font_size=ResponsiveHelper.get_font_size(32),
            color=(0.1, 0.4, 0.7, 1),
            bold=True,
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle'
        )
        form_container.add_widget(titulo)

        # Función para crear campos editables
        def crear_campo_editable(texto, valor_actual='', is_password=False):
            campo_layout = BoxLayout(
                orientation='vertical',
                spacing=dp(5),
                size_hint_y=None,
                size_hint_x=1
            )
            campo_layout.bind(minimum_height=campo_layout.setter('height'))

            campo_layout.add_widget(Label(
                text=texto,
                font_size=ResponsiveHelper.get_font_size(18),
                color=(0.1, 0.1, 0.2, 1),
                size_hint_y=None,
                size_hint_x=1,
                height=dp(30),
                halign='left'
            ))

            input_field = RoundedTextInput(
                text=valor_actual,
                size_hint_y=None,
                height=dp(55),
                password=is_password
            )
            campo_layout.add_widget(input_field)

            return campo_layout, input_field

        # Campos editables
        campos_edicion = [
            ('Nombre(s)', ''),
            ('Apellido Paterno', ''),
            ('Apellido Materno', ''),
            ('Usuario', ''),
            ('Correo Electrónico', ''),
            ('Nueva Contraseña (opcional)', '', True)
        ]

        # Añadir campos al formulario
        for item in campos_edicion:
            texto = item[0]
            valor = item[1] if len(item) > 1 else ''
            is_password = item[2] if len(item) > 2 else False
            
            layout, input_field = crear_campo_editable(texto, valor, is_password)
            
            # Nombres de atributos normalizados
            if texto == 'Nombre(s)':
                attr_name = 'nombre_input'
            elif texto == 'Apellido Paterno':
                attr_name = 'paterno_input'
            elif texto == 'Apellido Materno':
                attr_name = 'materno_input'
            elif texto == 'Usuario':
                attr_name = 'usuario_input'
            elif texto == 'Correo Electrónico':
                attr_name = 'correo_input'
            elif texto.startswith('Nueva Contraseña'):
                attr_name = 'nueva_contraseña_input'
            else:
                attr_name = texto.lower().replace(" ", "_").replace("(", "").replace(")", "") + "_input"
            
            setattr(self, attr_name, input_field)
            form_container.add_widget(layout)

        # Espaciador
        form_container.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # Contenedor de botones responsive
        botones_layout = BoxLayout(
            orientation=ResponsiveHelper.get_button_layout_orientation(),
            spacing=dp(15),
            size_hint_y=None,
            size_hint_x=1,
            height=ResponsiveHelper.get_button_layout_height()
        )

        # Botón Guardar Cambios
        btn_guardar = HoverButton(
            text='GUARDAR CAMBIOS',
            background_color=(0.1, 0.4, 0.7, 1)
        )
        btn_guardar.bind(on_press=self.guardar_cambios)
        botones_layout.add_widget(btn_guardar)

        # Botón Cancelar
        btn_cancelar = HoverButton(
            text='CANCELAR',
            background_color=(0.7, 0.1, 0.1, 1)
        )
        btn_cancelar.bind(on_press=self.cancelar)
        
        btn_cancelar.canvas.before.clear()
        with btn_cancelar.canvas.before:
            Color(0.7, 0.1, 0.1, 1)
            btn_cancelar.rect = RoundedRectangle(
                pos=btn_cancelar.pos,
                size=btn_cancelar.size,
                radius=[btn_cancelar.border_radius]
            )

        botones_layout.add_widget(btn_cancelar)

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

    def guardar_cambios(self, instance):
        """Validar y guardar los cambios en el backend"""
        # Validar campos obligatorios
        errores = []
        
        if not self.nombre_input.text.strip():
            errores.append("El nombre es obligatorio")
        
        if not self.paterno_input.text.strip():
            errores.append("El apellido paterno es obligatorio")
        
        if not self.usuario_input.text.strip():
            errores.append("El usuario es obligatorio")
        
        if not self.correo_input.text.strip():
            errores.append("El correo es obligatorio")
        
        # Validar formato de correo
        if self.correo_input.text.strip() and "@" not in self.correo_input.text:
            errores.append("El correo electrónico no es válido")
        
        # Validar contraseña solo si se ingresó una nueva
        nueva_pass = self.nueva_contraseña_input.text.strip()
        if nueva_pass and len(nueva_pass) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")
        
        if errores:
            self.mostrar_errores(errores)
            return
        
        # Preparar datos para actualizar
        payload = {
            'nombreAdministrador': self.nombre_input.text.strip(),
            'paternoAdministrador': self.paterno_input.text.strip(),
            'maternoAdministrador': self.materno_input.text.strip(),
            'usuarioAdministrador': self.usuario_input.text.strip(),
            'correoAdministrador': self.correo_input.text.strip()
        }
        
        # Solo incluir contraseña si se ingresó una nueva
        if nueva_pass:
            payload['contraseniaAdministrador'] = nueva_pass
        
        # Guardar en backend en un hilo separado
        def _save_task():
            try:
                admin_id = session.get_admin_id()
                print(f"[ActualizarDatosScreen] Actualizando admin ID: {admin_id}")
                print(f"[ActualizarDatosScreen] Payload: {payload}")
                
                # Llamar al endpoint de actualización
                updated_admin = api.update_administrador(admin_id, payload)
                
                # Actualizar sesión con los nuevos datos
                session.update_admin_data(updated_admin)
                
                def _success(dt):
                    self.mostrar_mensaje("Éxito", "Tus datos se han actualizado correctamente")
                    # Limpiar campo de contraseña
                    self.nueva_contraseña_input.text = ""
                    # Volver a la pantalla de cuenta después de 1.5 segundos
                    Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'cuenta'), 1.5)
                
                Clock.schedule_once(_success, 0)
                
            except Exception as e:
                print(f"[ActualizarDatosScreen] Error al guardar: {e}")
                error_msg = str(e)
                
                # Mensajes de error más amigables
                if "ya está registrado" in error_msg.lower():
                    error_msg = "El correo o usuario ya están en uso"
                elif "404" in error_msg:
                    error_msg = "No se encontró el administrador"
                elif "401" in error_msg or "403" in error_msg:
                    error_msg = "No tienes permisos para realizar esta acción"
                else:
                    error_msg = f"Error al actualizar: {error_msg}"
                
                def _error(dt):
                    self.mostrar_mensaje("Error", error_msg)
                
                Clock.schedule_once(_error, 0)
        
        # Ejecutar en hilo separado
        Thread(target=_save_task, daemon=True).start()

    def cancelar(self, instance):
        # Limpiar campo de contraseña al cancelar
        if hasattr(self, 'nueva_contraseña_input'):
            self.nueva_contraseña_input.text = ""
        self.manager.current = 'cuenta'

    def mostrar_errores(self, errores):
        """Mostrar popup de errores"""
        scroll_content = ScrollView(size_hint=(1, 1))
        lista_campos = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20), size_hint_y=None)
        lista_campos.bind(minimum_height=lista_campos.setter('height'))

        titulo_label = Label(
            text='Errores de Validación:',
            font_size=ResponsiveHelper.get_font_size(20),
            color=(0.5, 0.8, 1, 1),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        lista_campos.add_widget(titulo_label)

        for mensaje in errores:
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
        btn_cerrar.bind(on_press=popup.dismiss)

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
        popup.open()

    def mostrar_mensaje(self, titulo, mensaje):
        """Mostrar popup de mensaje"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))

        mensaje_label = Label(
            text=mensaje,
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.5, 0.8, 1, 1),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80)
        )
        mensaje_label.bind(size=mensaje_label.setter('text_size'))
        content.add_widget(mensaje_label)

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
        btn_aceptar.bind(on_press=popup.dismiss)
        content.add_widget(btn_aceptar)

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
            'nombreAdministrador': 'Admin',
            'paternoAdministrador': 'Test',
            'maternoAdministrador': 'Usuario',
            'usuarioAdministrador': 'admin',
            'correoAdministrador': 'admin@test.com'
        }
    )
    
    class TestApp(App):
        def build(self):
            sm = ScreenManager()
            sm.add_widget(ActualizarDatosScreen(name='actualizar'))
            return sm
    
    TestApp().run()