from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.utils import platform
from kivy.clock import Clock
from threading import Thread
from datetime import datetime
from api_client import api
from actualizar_torneos import ActualizarTorneoScreen

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
        if width < 600:
            return sp(base_size * 0.7)
        elif width < 900:
            return sp(base_size * 0.85)
        return sp(base_size)
    
    @staticmethod
    def get_card_height():
        """Retorna altura de tarjeta responsive"""
        width = Window.width
        if width < 600:
            return dp(320)
        elif width < 900:
            return dp(340)
        return dp(360)
    
    @staticmethod
    def get_button_height():
        """Retorna altura de botones responsive"""
        width = Window.width
        if width < 600:
            return dp(45)
        return dp(50)
    
    @staticmethod
    def get_grid_spacing():
        """Retorna espaciado del grid responsive"""
        width = Window.width
        if width < 600:
            return dp(10)
        elif width < 900:
            return dp(15)
        return dp(20)
    
    @staticmethod
    def get_grid_padding():
        """Retorna padding del grid responsive"""
        width = Window.width
        if width < 600:
            return dp(10)
        elif width < 900:
            return dp(15)
        return dp(20)
    
    @staticmethod
    def get_popup_size():
        """Retorna tamaño apropiado para popups"""
        width = Window.width
        height = Window.height
        if width < 600:
            return (width * 0.9, min(height * 0.45, dp(320)))
        else:
            return (min(width * 0.6, dp(500)), min(height * 0.4, dp(280)))


# ------------------ BOTONES CON ESTILOS ------------------
class HoverButton(Button):
    def __init__(self, **kwargs):
        bg_color = kwargs.pop('bg_color', (0.1, 0.4, 0.7, 1))
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = ResponsiveHelper.get_button_height()
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.bold = True
        self.border_radius = dp(12)
        self.original_color = bg_color

        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.border_radius])

        self.bind(pos=self.update_rect, size=self.update_rect)
        Window.bind(on_resize=self.on_window_resize)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_window_resize(self, instance, width, height):
        self.font_size = ResponsiveHelper.get_font_size(18)
        self.height = ResponsiveHelper.get_button_height()


class LightBlueButton(HoverButton):
    def __init__(self, **kwargs):
        super().__init__(bg_color=(0.2, 0.6, 1, 1), **kwargs)
        self.font_size = ResponsiveHelper.get_font_size(16)


class GreenButton(HoverButton):
    def __init__(self, **kwargs):
        super().__init__(bg_color=(0.2, 0.8, 0.2, 1), **kwargs)
        self.font_size = ResponsiveHelper.get_font_size(16)


# ------------------ POPUP DE CONFIRMACIÓN ------------------
class ConfirmDeletePopup(Popup):
    def __init__(self, torneo_data, on_confirm, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Confirmar Eliminación'
        self.title_color = (1, 1, 1, 1)
        self.title_size = ResponsiveHelper.get_font_size(22)
        self.title_align = 'center'
        self.size_hint = (None, None)
        self.size = ResponsiveHelper.get_popup_size()
        self.torneo_data = torneo_data
        self.on_confirm = on_confirm
        self.background = ''
        self.separator_height = 0
        self.auto_dismiss = False

        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        popup_width = self.size[0]
        message = Label(
            text=self._format_message(torneo_data["nombre"]),
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.5, 0.8, 1, 1),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(100),
            text_size=(popup_width - dp(40), None),
            shorten=False,
            markup=True
        )
        content.add_widget(message)

        buttons = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=ResponsiveHelper.get_button_height()
        )
        
        btn_cancel = Button(
            text='CANCELAR',
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(16)
        )
        btn_cancel.bind(on_press=self.dismiss)
        
        btn_confirm = Button(
            text='ELIMINAR',
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=ResponsiveHelper.get_font_size(16)
        )
        btn_confirm.bind(on_press=self.confirm_delete)
        
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_confirm)
        content.add_widget(buttons)

        self.content = content

        with self.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )

        self.bind(
            pos=lambda instance, value: setattr(self.rect, 'pos', value),
            size=lambda instance, value: setattr(self.rect, 'size', value)
        )

    def _format_message(self, nombre_torneo):
        max_len = 25
        if len(nombre_torneo) > max_len:
            mid_point = len(nombre_torneo) // 2
            split_point = nombre_torneo.rfind(' ', 0, mid_point + 10)
            if split_point == -1:
                split_point = mid_point
            nombre_formateado = (nombre_torneo[:split_point] + '\n' + 
                                nombre_torneo[split_point:])
        else:
            nombre_formateado = nombre_torneo
        
        return f'¿Estás seguro que deseas eliminar\nel torneo:\n"[b]{nombre_formateado}[/b]"?'

    def confirm_delete(self, instance):
        self.on_confirm(self.torneo_data)
        self.dismiss()


# ------------------ TARJETA DE TORNEO RESPONSIVE ------------------
class TorneoCard(BoxLayout):
    bg_color = ListProperty([0.1, 0.4, 0.7, 1])

    def __init__(self, torneo_data, on_delete, on_edit, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = [dp(20), dp(25), dp(20), dp(20)]
        self.size_hint = (1, None)
        self.height = ResponsiveHelper.get_card_height()
        self.torneo_data = torneo_data
        self.on_delete_callback = on_delete
        self.on_edit_callback = on_edit

        # Fondo con sombra
        with self.canvas.before:
            # Sombra
            Color(0.05, 0.2, 0.35, 0.3)
            self.shadow = RoundedRectangle(
                pos=(self.pos[0] + dp(3), self.pos[1] - dp(3)),
                size=self.size,
                radius=[dp(15)]
            )
            # Fondo principal
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15)])
            self.bind(pos=self.update_rect, size=self.update_rect)

        Window.bind(on_resize=self.on_window_resize)
        self.build_card()

    def build_card(self):
        self.clear_widgets()

        # Título con mejor espaciado
        self.title_label = Label(
            text=f"[b]{self.torneo_data['nombre']}[/b]",
            markup=True,
            font_size=ResponsiveHelper.get_font_size(22),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(45),
            halign='center',
            valign='middle'
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        self.add_widget(self.title_label)

        # Línea separadora decorativa
        separator = BoxLayout(size_hint_y=None, height=dp(2))
        with separator.canvas.before:
            Color(1, 1, 1, 0.3)
            separator.line = Rectangle(pos=separator.pos, size=separator.size)
        separator.bind(
            pos=lambda instance, value: setattr(separator.line, 'pos', value),
            size=lambda instance, value: setattr(separator.line, 'size', value)
        )
        self.add_widget(separator)

        # Información del torneo con iconos
        self.info_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=[dp(10), dp(15), dp(10), dp(10)]
        )
        self.info_layout.add_widget(self.create_info_row(f"  {self.torneo_data['fecha']}"))
        self.info_layout.add_widget(self.create_info_row(f"  {self.torneo_data['hora_inicio']} - {self.torneo_data['hora_fin']}"))
        self.info_layout.add_widget(self.create_info_row(f"  {self.torneo_data['Sede']}"))
        self.add_widget(self.info_layout)

        # Espaciador flexible
        self.add_widget(Label(size_hint_y=0.1))

        # Botón para ver combates
        self.combates_button = LightBlueButton(
            text='VER COMBATES',
            size_hint_y=None,
            height=ResponsiveHelper.get_button_height()
        )
        self.combates_button.bind(on_press=self.navigate_to_combates)
        self.add_widget(self.combates_button)

        # Botones de acción
        self.button_layout = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height=ResponsiveHelper.get_button_height(), 
            spacing=dp(10),
            padding=[0, dp(8), 0, 0]
        )
        
        self.edit_button = LightBlueButton(text='EDITAR', size_hint_x=0.5)
        self.edit_button.bind(on_press=self.open_edit_screen)
        
        self.delete_button = LightBlueButton(text='ELIMINAR', size_hint_x=0.5)
        # Cambiar color del botón eliminar
        self.delete_button.canvas.before.clear()
        with self.delete_button.canvas.before:
            Color(0.7, 0.1, 0.1, 1)
            self.delete_button.rect = RoundedRectangle(
                pos=self.delete_button.pos,
                size=self.delete_button.size,
                radius=[self.delete_button.border_radius]
            )
        self.delete_button.bind(on_press=self.open_delete_popup)
        
        self.button_layout.add_widget(self.edit_button)
        self.button_layout.add_widget(self.delete_button)
        self.add_widget(self.button_layout)

    def create_info_row(self, text):
        label = Label(
            text=text,
            font_size=ResponsiveHelper.get_font_size(16),
            color=(0.95, 0.95, 0.95, 1),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(30)
        )
        label.bind(size=label.setter('text_size'))
        return label

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.shadow.pos = (self.pos[0] + dp(3), self.pos[1] - dp(3))
        self.shadow.size = self.size

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.rebuild_card(), 0.1)
    
    def rebuild_card(self):
        self.height = ResponsiveHelper.get_card_height()
        self.build_card()

    def open_delete_popup(self, instance):
        ConfirmDeletePopup(
            torneo_data=self.torneo_data,
            on_confirm=self.on_delete_callback
        ).open()

    def open_edit_screen(self, instance):
        """
        CORREGIDO: Ahora pasa correctamente todos los datos del torneo,
        incluyendo el idTorneo que es crítico para el backend.
        """
        app = App.get_running_app()
        
        # Debug: imprimir los datos del torneo que se están pasando
        print(f"[DEBUG TorneoCard] Abriendo edición para torneo: {self.torneo_data}")
        print(f"[DEBUG TorneoCard] idTorneo: {self.torneo_data.get('idTorneo')}")
        
        # Remover la pantalla anterior si existe para forzar recarga
        if app.root.has_screen('actualizar_torneos'):
            app.root.remove_widget(app.root.get_screen('actualizar_torneos'))
        
        edit_screen = ActualizarTorneoScreen(
            name='actualizar_torneos',
            torneo_data=self.torneo_data, 
            on_save=self.on_edit_callback
        )
        
        app.root.add_widget(edit_screen)
        app.root.current = 'actualizar_torneos'

    def navigate_to_combates(self, instance):
        app = App.get_running_app()
        if not app.root.has_screen('combates_anteriores'):
            from combates_anteriore import CombatesScreen
            app.root.add_widget(CombatesScreen(name='combates_anteriores'))
        
        combates_screen = app.root.get_screen('combates_anteriores')
        combates_screen.torneo_nombre = self.torneo_data['nombre']
        combates_screen.torneo_id = self.torneo_data.get('idTorneo')
        
        # Solo rebuildeamos si el screen ya estaba creado
        if combates_screen in app.root.screens:
            combates_screen.build_ui()
        
        app.root.current = 'combates_anteriores'

# ------------------ PANTALLA DE TORNEOS ANTERIORES ------------------
class TorneosAnterioresScreen(Screen):

    def _map_torneo(self, t: dict) -> dict:
        """
        Mapea la respuesta del backend al formato que espera la UI.
        IMPORTANTE: Preserva el idTorneo para que esté disponible.
        """
        nombre = t.get("nombre") or f"Torneo #{t.get('idTorneo', 's/n')}"
        fecha = "—"
        hora_inicio = "—"
        hora_fin = "—" 

        fh = t.get("fechaHora")
        if fh:
            try:
                fh_clean = fh.replace('Z', '+00:00') if fh.endswith('Z') else fh
                dt = datetime.fromisoformat(fh_clean)
                fecha = dt.strftime('%d/%m/%Y')  # Cambiado a DD/MM/YYYY para consistencia
                hora_inicio = dt.strftime('%H:%M')
                # Nota: hora_fin no viene del backend, se calcula o se deja como "—"
            except Exception as e:
                print(f"[ERROR] Error parseando fechaHora '{fh}': {e}")
                pass

        mapped_data = {
            "nombre": nombre,
            "fecha": fecha,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "Sede": t.get("sede") or "—",
            "idTorneo": t.get("idTorneo"),  # ⭐ CRÍTICO: Preservar el ID
            "estado": t.get("estado"),
            "administrador": t.get("administrador")
        }
        
        print(f"[DEBUG] Torneo mapeado: {mapped_data}")
        return mapped_data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.torneos_data = []
        self.build_ui()
        Window.bind(on_resize=self.on_window_resize)

    def on_enter(self, *args):
        """Se ejecuta cada vez que se entra a esta pantalla"""
        self.fetch_torneos()

    def fetch_torneos(self):
        """Obtiene los torneos desde el backend"""
        self.torneos_data = []
        self.grid.clear_widgets()
        loading = Label(
            text="Cargando torneos...",
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.2, 0.4, 0.7, 1),
            size_hint_y=None,
            height=dp(40)
        )
        self.grid.add_widget(loading)

        def _task():
            try:
                print("[DEBUG] Solicitando torneos al backend...")
                resp = api.get_json("/apiTorneos/torneo")
                status = resp.status_code
                print(f"[DEBUG] Status code: {status}")
                
                if status == 200:
                    try:
                        data = resp.json() or []
                        print(f"[DEBUG] Torneos recibidos: {len(data)}")
                    except Exception as e:
                        print(f"[ERROR] Error parseando JSON: {e}")
                        data = []
                    
                    # Mapear datos
                    mapped = [self._map_torneo(t) for t in data]
                    
                    def _ok(dt):
                        self.torneos_data = mapped
                        self.populate_torneos()
                    Clock.schedule_once(_ok, 0)
                else:
                    def _err(dt):
                        self._show_error(f"Error {status} al consultar torneos.")
                    Clock.schedule_once(_err, 0)
            except Exception as e:
                print(f"[ERROR] Exception en fetch_torneos: {e}")
                def _err(dt, m=str(e)):
                    self._show_error(f"No se pudo obtener torneos.\n{m}")
                Clock.schedule_once(_err, 0)

        Thread(target=_task, daemon=True).start()

    def _show_error(self, msg: str):
        """Muestra un popup con mensaje de error"""
        popup = Popup(
            title="Error",
            size_hint=(None, None),
            size=ResponsiveHelper.get_popup_size()
        )
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        box.add_widget(Label(
            text=msg,
            halign='center',
            valign='middle',
            font_size=ResponsiveHelper.get_font_size(16)
        ))
        btn = Button(
            text="Cerrar",
            size_hint_y=None,
            height=dp(45),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        btn.bind(on_press=popup.dismiss)
        box.add_widget(btn)
        popup.content = box
        popup.open()

    def populate_torneos(self):
        """Llena el grid con las tarjetas de torneos"""
        self.grid.clear_widgets()
        if not self.torneos_data:
            self.grid.add_widget(Label(
                text="No hay torneos registrados",
                font_size=ResponsiveHelper.get_font_size(18),
                color=(0.2, 0.4, 0.7, 1),
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for torneo in self.torneos_data:
            card = TorneoCard(
                torneo_data=torneo,
                on_delete=self.delete_torneo,
                on_edit=self.edit_torneo
            )
            self.grid.add_widget(card)

    def build_ui(self):
        self.clear_widgets()
        
        self.layout = BoxLayout(orientation='vertical')

        # Fondo blanco suave
        with self.layout.canvas.before:
            Color(0.97, 0.97, 0.97, 1)
            self.rect = Rectangle(pos=self.layout.pos, size=self.layout.size)
            self.layout.bind(pos=self.update_rect, size=self.update_rect)

        # Header con mejor diseño
        header_height = dp(100) if Window.width >= 600 else dp(80)
        self.header = BoxLayout(
            size_hint_y=None,
            height=header_height,
            padding=[dp(20), dp(20), dp(20), dp(10)]
        )
        
        # Fondo del header con gradiente simulado
        with self.header.canvas.before:
            Color(0.1, 0.4, 0.7, 0.05)
            self.header_bg = Rectangle(pos=self.header.pos, size=self.header.size)
        
        def update_header_bg(instance, value):
            self.header_bg.pos = instance.pos
            self.header_bg.size = instance.size
        
        self.header.bind(pos=update_header_bg, size=update_header_bg)
        
        self.title_label = Label(
            text='Administrar Torneos',
            font_size=ResponsiveHelper.get_font_size(40),
            bold=True,
            color=(0.1, 0.4, 0.7, 1)
        )
        self.header.add_widget(self.title_label)
        self.layout.add_widget(self.header)

        # ScrollView con el grid de torneos
        self.scroll = ScrollView(
            bar_width=dp(10),
            bar_color=[0.2, 0.6, 1, 0.8],
            bar_inactive_color=[0.2, 0.6, 1, 0.4]
        )
        
        self.grid = GridLayout(
            cols=self.calculate_columns(),
            spacing=ResponsiveHelper.get_grid_spacing(),
            padding=ResponsiveHelper.get_grid_padding(),
            size_hint_y=None,
            row_default_height=ResponsiveHelper.get_card_height() + dp(10)
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        # Footer con botón volver
        footer_height = dp(80) if Window.width >= 600 else dp(70)
        self.footer = BoxLayout(
            size_hint_y=None,
            height=footer_height,
            padding=ResponsiveHelper.get_grid_padding()
        )

        btn_width = 0.3 if Window.width >= 900 else (0.5 if Window.width >= 600 else 0.7)
        self.btn_volver = HoverButton(
            text='VOLVER',
            bg_color=(0.1, 0.4, 0.7, 1),
            size_hint=(btn_width, 1),
            pos_hint={'center_x': 0.5}
        )
        self.btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'ini'))
        self.footer.add_widget(self.btn_volver)
        self.layout.add_widget(self.footer)

        self.add_widget(self.layout)

    def calculate_columns(self):
        """Calcula el número de columnas según el ancho de ventana"""
        width = Window.width
        if width > 1400:
            return 4
        elif width > 1000:
            return 3
        elif width > 600:
            return 2
        else:
            return 1

    def delete_torneo(self, torneo_a_eliminar: dict):
        """
        Handler que se ejecuta tras confirmar en el popup.
        Elimina el torneo del backend.
        """
        torneo_id = torneo_a_eliminar.get("idTorneo")

        # Si no hay id, borra local y sal
        if not torneo_id:
            self.torneos_data = [
                t for t in self.torneos_data
                if t.get('nombre') != torneo_a_eliminar.get('nombre')
            ]
            self.populate_torneos()
            return

        # Estado visual de "eliminando..."
        self.grid.clear_widgets()
        self.grid.add_widget(Label(
            text="Eliminando torneo...",
            font_size=ResponsiveHelper.get_font_size(18),
            color=(0.2, 0.4, 0.7, 1),
            size_hint_y=None,
            height=dp(40)
        ))

        def _task():
            try:
                print(f"[DEBUG] Eliminando torneo ID: {torneo_id}")
                resp = api.delete(f"/apiTorneos/torneo/{torneo_id}")
                print(f"[DEBUG] Status code delete: {resp.status_code}")
                
                if resp.status_code in (200, 204):
                    # Éxito: refrescar lista desde el backend
                    def _ok(dt):
                        self.fetch_torneos()
                    Clock.schedule_once(_ok, 0)
                else:
                    def _err(dt):
                        self._show_error(f"No se pudo eliminar (HTTP {resp.status_code}).")
                        self.fetch_torneos()
                    Clock.schedule_once(_err, 0)
            except Exception as e:
                print(f"[ERROR] Exception eliminando torneo: {e}")
                def _err(dt, m=str(e)):
                    self._show_error(f"Error eliminando torneo:\n{m}")
                    self.fetch_torneos()
                Clock.schedule_once(_err, 0)

        Thread(target=_task, daemon=True).start()

    def edit_torneo(self, torneo_original, nuevos_datos):
        """
        Callback que se ejecuta después de editar un torneo.
        Simplemente refresca la lista desde el backend.
        """
        print(f"[DEBUG] edit_torneo callback ejecutado")
        print(f"[DEBUG] Torneo original: {torneo_original}")
        print(f"[DEBUG] Nuevos datos: {nuevos_datos}")
        
        # Refrescar la lista completa desde el backend
        self.fetch_torneos()

    def update_rect(self, *args):
        self.rect.pos = self.layout.pos
        self.rect.size = self.layout.size

    def on_window_resize(self, instance, width, height):
        Clock.schedule_once(lambda dt: self.rebuild_ui(), 0.1)
    
    def rebuild_ui(self):
        # Actualizar número de columnas
        self.grid.cols = self.calculate_columns()
        self.grid.spacing = ResponsiveHelper.get_grid_spacing()
        self.grid.padding = ResponsiveHelper.get_grid_padding()
        self.grid.row_default_height = ResponsiveHelper.get_card_height() + dp(10)
        
        # Reconstruir UI completa para ajustar tamaños
        self.build_ui()


# ------------------ APLICACIÓN ------------------
class TorneosApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TorneosAnterioresScreen(name='torneos_anteriores'))
        return sm


if __name__ == '__main__':
    TorneosApp().run()