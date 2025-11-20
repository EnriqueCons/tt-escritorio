from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.utils import platform
from kivy.clock import Clock
from kivy.animation import Animation
from api_client import api
from threading import Thread


# ------------------ UTILIDADES RESPONSIVE ------------------
class ResponsiveHelper:
    @staticmethod
    def is_mobile():
        return platform in ['android', 'ios']
    
    @staticmethod
    def is_desktop():
        return platform in ['win', 'linux', 'macosx']
    
    @staticmethod
    def get_card_width():
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
        width = Window.width
        if width < 600:
            return sp(base_size * 0.8)
        elif width < 900:
            return sp(base_size * 0.9)
        return sp(base_size)
    
    @staticmethod
    def get_popup_size():
        width = Window.width
        height = Window.height
        if width < 600:
            return (width * 0.9, min(height * 0.4, dp(250)))
        else:
            return (min(width * 0.6, dp(450)), min(height * 0.35, dp(250)))
    
    @staticmethod
    def get_button_orientation():
        return 'horizontal' if Window.width > 600 else 'vertical'
    
    @staticmethod
    def get_button_height():
        return dp(50) if Window.width > 600 else dp(110)


class LightBlueButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = ResponsiveHelper.get_font_size(16)
        self.bold = True
        self.border_radius = dp(12)
        self.original_height = dp(50)

        with self.canvas.before:
            Color(0.2, 0.6, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.border_radius])

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(on_press=self.on_button_press)
        self.bind(on_release=self.on_button_release)
        Window.bind(on_resize=self.on_window_resize)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_window_resize(self, instance, width, height):
        self.font_size = ResponsiveHelper.get_font_size(16)

    def on_button_press(self, instance):
        # Animación al presionar: reducir ligeramente el tamaño
        anim = Animation(
            size=(self.width * 0.95, self.height * 0.95),
            duration=0.1
        )
        anim.start(self)

    def on_button_release(self, instance):
        # Animación al soltar: volver al tamaño original
        anim = Animation(
            size=(self.width / 0.95, self.height / 0.95),
            duration=0.1
        )
        anim.start(self)


class SuccessPopup(Popup):
    message = StringProperty('')
    
    def __init__(self, message, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.title = 'Éxito'
        self.title_color = (1, 1, 1, 1)
        self.title_size = ResponsiveHelper.get_font_size(22)
        self.title_align = 'center'
        self.size_hint = (None, None)
        self.size = ResponsiveHelper.get_popup_size()
        self.background = ''
        self.separator_height = 0
        self.auto_dismiss = True

        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(25))
        
        message_label = Label(
            text=self.message,
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.5, 0.8, 1, 1),
            halign='center',
            valign='middle'
        )
        message_label.bind(size=message_label.setter('text_size'))
        content.add_widget(message_label)
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(18))
        btn_ok.bind(on_press=self.dismiss)
        
        content.add_widget(btn_ok)
        self.content = content

        with self.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(20)])

        self.bind(
            pos=lambda instance, value: setattr(self.rect, 'pos', value),
            size=lambda instance, value: setattr(self.rect, 'size', value)
        )


class PasswordInputPopup(Popup):
    def __init__(self, on_verify, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Ingresar Contraseña'
        self.title_color = (1, 1, 1, 1)
        self.title_size = ResponsiveHelper.get_font_size(22)
        self.title_align = 'center'
        self.size_hint = (None, None)
        self.size = ResponsiveHelper.get_popup_size()
        self.on_verify = on_verify
        self.background = ''
        self.separator_height = 0
        self.auto_dismiss = False

        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(25))
        
        self.password_input = TextInput(
            password=True,
            multiline=False,
            font_size=ResponsiveHelper.get_font_size(18),
            size_hint_y=None,
            height=dp(50),
            hint_text='Ingrese su contraseña',
            padding=[dp(15), dp(12)]
        )
        content.add_widget(self.password_input)
        
        buttons = BoxLayout(
            orientation=ResponsiveHelper.get_button_orientation(),
            spacing=dp(15),
            size_hint_y=None,
            height=ResponsiveHelper.get_button_height()
        )
        
        btn_cancel = Button(
            text='CANCELAR',
            size_hint_x=0.5 if Window.width > 600 else 1,
            background_normal='',
            background_color=(0.7, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(18))
        btn_cancel.bind(on_press=self.dismiss)
        
        btn_verify = Button(
            text='VERIFICAR',
            size_hint_x=0.5 if Window.width > 600 else 1,
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(18))
        btn_verify.bind(on_press=self.verify_password)
        
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_verify)
        content.add_widget(buttons)
        
        self.content = content

        with self.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(20)])

        self.bind(
            pos=lambda instance, value: setattr(self.rect, 'pos', value),
            size=lambda instance, value: setattr(self.rect, 'size', value)
        )

    def verify_password(self, instance):
        if self.password_input.text == "petotech123":
            self.on_verify(True)
            self.dismiss()
        else:
            self.password_input.text = ''
            self.password_input.hint_text = 'Contraseña incorrecta, intente de nuevo'
            self.password_input.hint_text_color = (1, 0, 0, 1)


class PasswordDisplayPopup(Popup):
    def __init__(self, combate_numero, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Contraseña del Combate'
        self.title_color = (1, 1, 1, 1)
        self.title_size = ResponsiveHelper.get_font_size(22)
        self.title_align = 'center'
        self.size_hint = (None, None)
        self.size = ResponsiveHelper.get_popup_size()
        self.background = ''
        self.separator_height = 0
        self.auto_dismiss = True

        self.combate_password = self._generate_password(combate_numero)

        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(25))
        
        message = Label(
            text=f'Contraseña para:\n[b]Combate #{combate_numero}[/b]',
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.5, 0.8, 1, 1),
            halign='center',
            markup=True
        )
        content.add_widget(message)
        
        password_display = Label(
            text=f'[b]{self.combate_password}[/b]',
            font_size=ResponsiveHelper.get_font_size(26),
            color=(1, 1, 1, 1),
            halign='center',
            markup=True
        )
        content.add_widget(password_display)
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(18))
        btn_ok.bind(on_press=self.dismiss)
        
        content.add_widget(btn_ok)
        self.content = content

        with self.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(20)])

        self.bind(
            pos=lambda instance, value: setattr(self.rect, 'pos', value),
            size=lambda instance, value: setattr(self.rect, 'size', value)
        )

    def _generate_password(self, combate_numero):
        import hashlib
        hash_obj = hashlib.md5(str(combate_numero).encode())
        return hash_obj.hexdigest()[:8].upper()


class ConfirmDeleteCombatePopup(Popup):
    def __init__(self, combate_data, on_confirm, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Confirmar Eliminación'
        self.title_color = (1, 1, 1, 1)
        self.title_size = ResponsiveHelper.get_font_size(22)
        self.title_align = 'center'
        self.size_hint = (None, None)
        self.size = ResponsiveHelper.get_popup_size()
        self.combate_data = combate_data
        self.on_confirm = on_confirm
        self.background = ''
        self.separator_height = 0
        self.auto_dismiss = False

        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(25))
        
        popup_size = ResponsiveHelper.get_popup_size()
        text_width = popup_size[0] - dp(50)
        
        message = Label(
            text=f'¿Estás seguro que deseas eliminar\nel combate #{combate_data["numero"]}?\nCategoría: {combate_data["categoria"]}',
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.5, 0.8, 1, 1),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(100),
            text_size=(text_width, None)
        )
        content.add_widget(message)

        buttons = BoxLayout(
            orientation=ResponsiveHelper.get_button_orientation(),
            spacing=dp(15),
            size_hint_y=None,
            height=ResponsiveHelper.get_button_height()
        )
        
        btn_cancel = Button(
            text='CANCELAR',
            size_hint_x=0.5 if Window.width > 600 else 1,
            background_normal='',
            background_color=(0.7, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(18))
        btn_cancel.bind(on_press=self.dismiss)
        
        btn_confirm = Button(
            text='ELIMINAR',
            size_hint_x=0.5 if Window.width > 600 else 1,
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(18))
        btn_confirm.bind(on_press=self.confirm_delete)
        
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_confirm)
        content.add_widget(buttons)

        self.content = content

        with self.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(20)])

        self.bind(
            pos=lambda instance, value: setattr(self.rect, 'pos', value),
            size=lambda instance, value: setattr(self.rect, 'size', value)
        )

    def confirm_delete(self, instance):
        self.on_confirm(self.combate_data)
        self.dismiss()


class CombateCard(BoxLayout):
    bg_color = ListProperty([0.1, 0.4, 0.7, 1])

    def __init__(self, combate_data, on_delete, on_edit, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self.padding = [dp(25), dp(20)]
        self.size_hint = (ResponsiveHelper.get_card_width(), None)
        self.pos_hint = {'center_x': 0.5}
        self.combate_data = combate_data
        self.on_delete_callback = on_delete
        self.on_edit_callback = on_edit
        
        self.build_card()
        Window.bind(on_resize=self.on_window_resize)

    def build_card(self):
        self.clear_widgets()
        
        # Calcular altura según orientación de botones (más compacto)
        button_rows_height = dp(110) if Window.width > 600 else dp(220)
        self.height = dp(180) + button_rows_height

        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
            
            self.bind(pos=self.update_graphics, size=self.update_graphics)

        # Título con badge del número de combate (más compacto)
        header_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        # Badge del número
        badge_label = Label(
            text=f'#{self.combate_data["numero"]}',
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.2, 0.6, 1, 1),
            size_hint=(None, None),
            size=(dp(55), dp(35)),
            bold=True
        )
        
        with badge_label.canvas.before:
            Color(1, 1, 1, 0.95)
            badge_label.badge_rect = RoundedRectangle(
                pos=badge_label.pos, 
                size=badge_label.size, 
                radius=[dp(8)]
            )
            badge_label.bind(
                pos=lambda inst, val: setattr(inst.badge_rect, 'pos', val),
                size=lambda inst, val: setattr(inst.badge_rect, 'size', val)
            )
        
        header_box.add_widget(badge_label)
        header_box.add_widget(BoxLayout())  # Spacer
        
        self.add_widget(header_box)

        # Información del combate
        self.info_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(6),
            padding=[dp(5), dp(2), dp(5), dp(2)]
        )
        
        self.add_info_row("Fecha:", self.combate_data['fecha'])
        self.add_info_row("Hora:", self.combate_data.get('hora', 'No disponible'))
        self.add_info_row("Categoría:", self.combate_data['categoria'])

        participantes_text = (
            f"[color=5BC0EB]{self.combate_data.get('competidor1', 'No disponible')}[/color] vs "
            f"[color=ff3333]{self.combate_data.get('competidor2', 'No disponible')}[/color]"
        )
        self.add_info_row("Participantes:", participantes_text, is_participants=True)

        self.add_widget(self.info_layout)

        # Botones responsive sin iconos
        if Window.width > 600:
            self.create_horizontal_buttons()
        else:
            self.create_vertical_buttons()

    def create_horizontal_buttons(self):
        buttons_main_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            height=dp(110)
        )

        button_row1 = BoxLayout(orientation='horizontal', spacing=dp(12), size_hint_y=None, height=dp(50))
        edit_btn = LightBlueButton(text='EDITAR')
        edit_btn.bind(on_press=self.open_edit_screen)
        delete_btn = LightBlueButton(text='ELIMINAR')
        delete_btn.bind(on_press=self.open_delete_popup)
        button_row1.add_widget(edit_btn)
        button_row1.add_widget(delete_btn)

        button_row2 = BoxLayout(orientation='horizontal', spacing=dp(12), size_hint_y=None, height=dp(50))
        password_btn = LightBlueButton(text='CONTRASEÑA')
        password_btn.bind(on_press=self.open_password_flow)
        tablero_btn = LightBlueButton(text='TABLERO')
        tablero_btn.bind(on_press=self.navigate_to_tablero)
        button_row2.add_widget(password_btn)
        button_row2.add_widget(tablero_btn)

        buttons_main_layout.add_widget(button_row1)
        buttons_main_layout.add_widget(button_row2)
        self.add_widget(buttons_main_layout)

    def create_vertical_buttons(self):
        buttons_main_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            height=dp(220)
        )

        edit_btn = LightBlueButton(text='EDITAR')
        edit_btn.bind(on_press=self.open_edit_screen)
        buttons_main_layout.add_widget(edit_btn)

        delete_btn = LightBlueButton(text='ELIMINAR')
        delete_btn.bind(on_press=self.open_delete_popup)
        buttons_main_layout.add_widget(delete_btn)

        password_btn = LightBlueButton(text='CONTRASEÑA')
        password_btn.bind(on_press=self.open_password_flow)
        buttons_main_layout.add_widget(password_btn)

        tablero_btn = LightBlueButton(text='TABLERO')
        tablero_btn.bind(on_press=self.navigate_to_tablero)
        buttons_main_layout.add_widget(tablero_btn)

        self.add_widget(buttons_main_layout)

    def add_info_row(self, label, value, is_participants=False):
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(28), spacing=dp(8))
        
        lbl_label = Label(
            text=label,
            font_size=ResponsiveHelper.get_font_size(14),
            color=(0.95, 0.95, 0.95, 0.9),
            halign='left',
            valign='middle',
            size_hint_x=0.35 if Window.width < 600 else 0.3,
            text_size=(None, None),
            bold=True
        )
        
        card_width = Window.width * ResponsiveHelper.get_card_width() - dp(60)
        value_width = card_width * (0.65 if Window.width < 600 else 0.7)
        
        lbl_value = Label(
            text=value,
            font_size=ResponsiveHelper.get_font_size(13 if Window.width < 600 else 14),
            color=(1, 1, 1, 1) if not is_participants else (1, 1, 1, 1),
            halign='left',
            valign='middle',
            size_hint_x=0.65 if Window.width < 600 else 0.7,
            text_size=(value_width, None),
            shorten=False,
            markup=True
        )
        
        row.add_widget(lbl_label)
        row.add_widget(lbl_value)
        self.info_layout.add_widget(row)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.rebuild_card(), 0.1)

    def rebuild_card(self):
        self.size_hint = (ResponsiveHelper.get_card_width(), None)
        self.build_card()

    def open_delete_popup(self, instance):
        ConfirmDeleteCombatePopup(
            combate_data=self.combate_data,
            on_confirm=self.on_delete_callback
        ).open()

    def open_edit_screen(self, instance):
        app = App.get_running_app()
        if not app.root.has_screen('actualizar_combate'):
            from actualizar_combate import ActualizarCombateScreen
            app.root.add_widget(ActualizarCombateScreen(
                name='actualizar_combate',
                combate_data=self.combate_data,
                on_save=self.on_edit_callback
            ))
        app.root.current = 'actualizar_combate'

    def open_password_flow(self, instance):
        PasswordInputPopup(
            on_verify=lambda success: self.show_combate_password() if success else None
        ).open()

    def show_combate_password(self):
        PasswordDisplayPopup(combate_numero=self.combate_data['numero']).open()

    def navigate_to_tablero(self, instance):
        app = App.get_running_app()
        if not app.root.has_screen('tablero'):
            from tablero import MainScreentab
            app.root.add_widget(MainScreentab(name='tablero'))
        
        tablero_screen = app.root.get_screen('tablero')
        tablero_screen.com1_panel.name = self.combate_data.get('competidor1', 'COM1')
        tablero_screen.com2_panel.name = self.combate_data.get('competidor2', 'COM2')
        tablero_screen.com1_panel.nationality = self.combate_data.get('nacionalidad1', '')
        tablero_screen.com2_panel.nationality = self.combate_data.get('nacionalidad2', '')
        
        app.root.current = 'tablero'

class CombatesScreen(Screen):
    """
    Pantalla que muestra todos los combates de un torneo.
    Conectada a la API REST para operaciones CRUD.
    """
    torneo_nombre = StringProperty('')
    torneo_id = NumericProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.combates = []
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)
        print(f"[CombatesScreen] Inicializado para torneo: {self.torneo_nombre} (ID: {self.torneo_id})")

    def build_ui(self):
        self.clear_widgets()
        
        self.layout = BoxLayout(orientation='vertical')
        
        with self.layout.canvas.before:
            Color(0.95, 0.97, 1, 1)
            self.rect = RoundedRectangle(pos=self.layout.pos, size=self.layout.size)
            self.layout.bind(pos=self.update_rect, size=self.update_rect)

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(90), padding=[dp(20), dp(15)])
        header_content = BoxLayout(orientation='vertical', spacing=dp(5))
        
        titulo = Label(
            text=f"[b]Combates del Torneo[/b]",
            markup=True,
            font_size=ResponsiveHelper.get_font_size(24),
            color=(0.1, 0.4, 0.7, 1),
            halign='center',
            valign='bottom',
            size_hint_y=0.6
        )
        
        subtitulo = Label(
            text=self.torneo_nombre,
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.2, 0.5, 0.8, 1),
            halign='center',
            valign='top',
            size_hint_y=0.4
        )
        
        header_content.add_widget(titulo)
        header_content.add_widget(subtitulo)
        header.add_widget(header_content)
        self.layout.add_widget(header)
        
        # ScrollView
        scroll = ScrollView(
            size_hint=(1, 1),
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            bar_color=(0.2, 0.6, 1, 0.8),
            bar_inactive_color=(0.2, 0.6, 1, 0.3),
            do_scroll_x=False,
            effect_cls='ScrollEffect'
        )
        
        self.grid = GridLayout(
            cols=1,
            spacing=dp(20),
            padding=[dp(15), dp(25), dp(15), dp(25)],
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        scroll.add_widget(self.grid)
        self.layout.add_widget(scroll)

        # Footer
        footer = BoxLayout(size_hint_y=None, height=dp(70), padding=[dp(30), dp(15), dp(30), dp(15)])
        btn_volver = Button(
            text="Volver",
            font_size=ResponsiveHelper.get_font_size(18),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            on_press=lambda x: setattr(self.manager, 'current', 'torneos_anteriores')
        )
        
        with btn_volver.canvas.before:
            Color(0.2, 0.6, 1, 1)
            btn_volver.btn_rect = RoundedRectangle(pos=btn_volver.pos, size=btn_volver.size, radius=[dp(12)])
            btn_volver.bind(
                pos=lambda inst, val: setattr(inst.btn_rect, 'pos', val),
                size=lambda inst, val: setattr(inst.btn_rect, 'size', val)
            )
        
        footer.add_widget(btn_volver)
        self.layout.add_widget(footer)
        
        self.add_widget(self.layout)
        
        # IMPORTANTE: Cargar combates desde la API
        self.load_combates()

    def update_rect(self, *args):
        self.rect.pos = self.layout.pos
        self.rect.size = self.layout.size

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)

    def load_combates(self):
        """Carga los combates desde la API"""
        print("[CombatesScreen] Iniciando carga de combates...")
        self.grid.clear_widgets()
        
        # Mostrar indicador de carga
        loading_label = Label(
            text='Cargando combates...',
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.2, 0.6, 1, 1)
        )
        self.grid.add_widget(loading_label)
        
        # Hacer la petición en un thread separado
        thread = Thread(target=self._fetch_combates)
        thread.daemon = True
        thread.start()

    def _fetch_combates(self):
        """Obtiene los combates de la API en segundo plano"""
        print("[CombatesScreen] Fetching combates from API...")
        try:
            # Usar el cliente API
            combates_data = api.get_all_combates()
            print(f"[CombatesScreen] Recibidos {len(combates_data)} combates de la API")
            
            # Filtrar por torneo_id si es necesario
            if self.torneo_id:
                combates_data = [
                    c for c in combates_data 
                    if c.get('torneo_id') == self.torneo_id
                ]
                print(f"[CombatesScreen] Después del filtro por torneo_id={self.torneo_id}: {len(combates_data)} combates")
            
            # Transformar los datos al formato que espera tu UI
            self.combates = [self._transform_combate(c) for c in combates_data]
            print(f"[CombatesScreen] Combates transformados: {len(self.combates)}")
            
            # Actualizar la UI en el hilo principal
            Clock.schedule_once(lambda dt: self._display_combates())
                
        except RuntimeError as e:
            print(f"[CombatesScreen] RuntimeError: {e}")
            Clock.schedule_once(
                lambda dt: self._show_error(str(e))
            )
        except Exception as e:
            print(f"[CombatesScreen] Exception: {type(e).__name__}: {e}")
            error_msg = "No se pudo conectar al servidor" if "Connection" in str(e) else f"Error: {str(e)}"
            Clock.schedule_once(
                lambda dt: self._show_error(error_msg)
            )

    def _transform_combate(self, api_data):
        """Transforma los datos de la API al formato que espera la UI"""
        return {
            "id": api_data.get("idCombate"),
            "numero": api_data.get("idCombate"),
            "fecha": self._format_date(api_data.get("horaCombate")),
            "hora": self._format_time(api_data.get("horaCombate")),
            "categoria": api_data.get("area", "Sin categoría"),
            
            # Competidor Rojo
            "competidor1": api_data.get("competidorRojo", {}).get("nombres", "No disponible"),
            "fecha_nac1": self._format_date_simple(api_data.get("competidorRojo", {}).get("fechaNacimiento", "")),
            "peso1": api_data.get("competidorRojo", {}).get("pesoKg", 0),
            "sexo1": api_data.get("competidorRojo", {}).get("sexo", ""),
            "nacionalidad1": "Mexicana",
            
            # Competidor Azul
            "competidor2": api_data.get("competidorAzul", {}).get("nombres", "No disponible"),
            "fecha_nac2": self._format_date_simple(api_data.get("competidorAzul", {}).get("fechaNacimiento", "")),
            "peso2": api_data.get("competidorAzul", {}).get("pesoKg", 0),
            "sexo2": api_data.get("competidorAzul", {}).get("sexo", ""),
            "nacionalidad2": "Mexicana",
            
            # Detalles del combate
            "area": api_data.get("area", "Sin área"),
            "num_rounds": api_data.get("numeroRound", 0),
            "duracion_round": self._parse_duration(api_data.get("duracionRound")),
            "duracion_descanso": self._parse_duration(api_data.get("duracionDescanso")),
            "estado": api_data.get("estado", "PENDIENTE"),
            
            # Jueces
            "arbitro_nombre": api_data.get("jueces", {}).get("arbitroCentral", {}).get("nombres", ""),
            "arbitro_Apellidos": api_data.get("jueces", {}).get("arbitroCentral", {}).get("apellidos", ""),
            "juez1_nombre": api_data.get("jueces", {}).get("juez1", {}).get("nombres", ""),
            "juez1_Apellidos": api_data.get("jueces", {}).get("juez1", {}).get("apellidos", ""),
            "juez2_nombre": api_data.get("jueces", {}).get("juez2", {}).get("nombres", ""),
            "juez2_Apellidos": api_data.get("jueces", {}).get("juez2", {}).get("apellidos", ""),
            "juez3_nombre": api_data.get("jueces", {}).get("juez3", {}).get("nombres", ""),
            "juez3_Apellidos": api_data.get("jueces", {}).get("juez3", {}).get("apellidos", ""),
            
            "torneo_id": self.torneo_id
        }

    def _format_date(self, datetime_str):
        """Formatea la fecha desde ISO 8601 a formato dd/mm/yyyy"""
        if not datetime_str:
            return "Sin fecha"
        try:
            from datetime import datetime
            # Manejar diferentes formatos
            if 'T' in str(datetime_str):
                dt = datetime.fromisoformat(str(datetime_str).replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(str(datetime_str), "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except:
            return "Sin fecha"

    def _format_date_simple(self, date_str):
        """Formatea una fecha simple YYYY-MM-DD a DD/MM/YYYY"""
        if not date_str:
            return ""
        try:
            from datetime import datetime
            if isinstance(date_str, str):
                if 'T' in date_str:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                return dt.strftime("%d/%m/%Y")
            return str(date_str)
        except:
            return str(date_str)

    def _format_time(self, datetime_str):
        """Extrae la hora desde ISO 8601"""
        if not datetime_str:
            return "Sin hora"
        try:
            from datetime import datetime
            if 'T' in str(datetime_str):
                dt = datetime.fromisoformat(str(datetime_str).replace('Z', '+00:00'))
                return dt.strftime("%H:%M")
            return "Sin hora"
        except:
            return "Sin hora"

    def _parse_duration(self, time_str):
        """Convierte LocalTime (HH:mm:ss) a minutos"""
        if not time_str:
            return 0
        try:
            parts = str(time_str).split(':')
            if len(parts) >= 2:
                return int(parts[0]) * 60 + int(parts[1])
            return 0
        except:
            return 0

    def _display_combates(self):
        """Muestra los combates en la UI (se ejecuta en el hilo principal)"""
        self.grid.clear_widgets()
        
        if not self.combates:
            no_data_label = Label(
                text='No hay combates registrados',
                font_size=ResponsiveHelper.get_font_size(18),
                color=(0.5, 0.5, 0.5, 1)
            )
            self.grid.add_widget(no_data_label)
            return
        
        for combate in self.combates:
            card = CombateCard(
                combate_data=combate,
                on_delete=self.delete_combate,
                on_edit=self.edit_combate
            )
            self.grid.add_widget(card)

    def _show_error(self, message):
        """Muestra un mensaje de error en la UI"""
        self.grid.clear_widgets()
        
        error_box = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
            height=dp(150)
        )
        
        error_label = Label(
            text=message,
            font_size=ResponsiveHelper.get_font_size(16),
            color=(1, 0, 0, 1),
            halign='center',
            valign='middle'
        )
        error_label.bind(size=error_label.setter('text_size'))
        error_box.add_widget(error_label)
        
        # Botón para reintentar
        retry_btn = Button(
            text='Reintentar',
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(16)
        )
        retry_btn.bind(on_press=lambda x: self.load_combates())
        error_box.add_widget(retry_btn)
        
        self.grid.add_widget(error_box)

    def delete_combate(self, combate_data):
        """Elimina un combate mediante la API usando ApiClient"""
        combate_id = combate_data['id']
        
        def _do_delete():
            try:
                success = api.delete_combate(combate_id)
                if success:
                    Clock.schedule_once(lambda dt: self._on_delete_success(combate_data))
                else:
                    Clock.schedule_once(
                        lambda dt: self.show_message("Error", "No se pudo eliminar el combate")
                    )
            except RuntimeError as e:
                Clock.schedule_once(
                    lambda dt: self.show_message("Error", str(e))
                )
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self.show_message("Error", f"Error al eliminar: {str(e)}")
                )
        
        thread = Thread(target=_do_delete)
        thread.daemon = True
        thread.start()

    def _on_delete_success(self, combate_data):
        """Callback cuando se elimina exitosamente"""
        self.show_message("Éxito", f"Combate #{combate_data['numero']} eliminado correctamente")
        self.load_combates()

    def edit_combate(self, combate_original, nuevos_datos):
        """Actualiza un combate mediante la API usando ApiClient"""
        combate_id = combate_original['id']
        
        def _do_update():
            try:
                # Transformar los datos al formato que espera tu API
                payload = {
                    "area": nuevos_datos.get("area", combate_original["area"]),
                    "numeroRound": nuevos_datos.get("num_rounds", combate_original["num_rounds"]),
                    "duracionRound": self._minutes_to_time(nuevos_datos.get("duracion_round", combate_original["duracion_round"])),
                    "duracionDescanso": self._minutes_to_time(nuevos_datos.get("duracion_descanso", combate_original["duracion_descanso"])),
                    "estado": nuevos_datos.get("estado", combate_original["estado"]),
                }
                
                result = api.update_combate(combate_id, payload)
                if result:
                    Clock.schedule_once(lambda dt: self._on_update_success(combate_original))
                else:
                    Clock.schedule_once(
                        lambda dt: self.show_message("Error", "No se pudo actualizar el combate")
                    )
            except RuntimeError as e:
                Clock.schedule_once(
                    lambda dt: self.show_message("Error", str(e))
                )
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self.show_message("Error", f"Error al actualizar: {str(e)}")
                )
        
        thread = Thread(target=_do_update)
        thread.daemon = True
        thread.start()

    def _minutes_to_time(self, minutes):
        """Convierte minutos a formato HH:mm:ss"""
        if not minutes:
            return "00:00:00"
        hours = int(minutes) // 60
        mins = int(minutes) % 60
        return f"{hours:02d}:{mins:02d}:00"

    def _on_update_success(self, combate_original):
        """Callback cuando se actualiza exitosamente"""
        self.show_message("Éxito", f"Combate #{combate_original['numero']} actualizado correctamente")
        self.load_combates()

    def show_message(self, title, message):
        """Muestra un popup con un mensaje"""
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(25))
        
        popup_size = ResponsiveHelper.get_popup_size()
        text_width = popup_size[0] - dp(50)
        
        lbl_mensaje = Label(
            text=message,
            color=(0.5, 0.8, 1, 1),
            font_size=ResponsiveHelper.get_font_size(18),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80),
            text_size=(text_width, None)
        )
        lbl_mensaje.bind(size=lbl_mensaje.setter('text_size'))
        content.add_widget(lbl_mensaje)

        btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        
        btn_aceptar = Button(
            text='ACEPTAR',
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(18))
        btn_aceptar.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(btn_aceptar)

        content.add_widget(btn_layout)

        popup = Popup(
            title=title,
            title_color=(1, 1, 1, 1),
            title_size=ResponsiveHelper.get_font_size(22),
            title_align='center',
            content=content,
            size_hint=(None, None),
            size=popup_size,
            separator_height=0,
            background='',
            auto_dismiss=False
        )

        with popup.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            popup.rect = RoundedRectangle(pos=popup.pos, size=popup.size, radius=[dp(20)])

        popup.bind(
            pos=lambda instance, value: setattr(popup.rect, 'pos', value),
            size=lambda instance, value: setattr(popup.rect, 'size', value)
        )

        popup.open()