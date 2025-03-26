from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.base import EventLoop
from kivy.metrics import dp  # Import density-independent pixels
import random
import string

# Try to import from password_manager, fall back to local implementations
try:
    from password_manager import (
        store_password, 
        recover_password, 
        list_credentials, 
        verify_admin_password,
        delete_password
    )
except ImportError as e:
    print(f"Import warning: {e}")
    def missing_function(*args, **kwargs):
        raise NotImplementedError("Password manager function not available")
    store_password = recover_password = list_credentials = verify_admin_password = delete_password = missing_function

def generate_password(length=16, use_upper=True, use_lower=True, use_numbers=True, use_special=True):
    """Generate a random password with specified characteristics"""
    characters = []
    if use_upper: characters.extend(string.ascii_uppercase)
    if use_lower: characters.extend(string.ascii_lowercase)
    if use_numbers: characters.extend(string.digits)
    if use_special: characters.extend('!@#$%^&*()_+-=[]{}|;:,.<>?')
    if not characters:
        raise ValueError("At least one character type must be selected")
    return ''.join(random.choice(characters) for _ in range(length))

class CustomTabbedPanelItem(TabbedPanelItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = [20, 5]  # [horizontal, vertical]
        label = Label(text=kwargs.get('text', ''), 
                     size_hint_x=None, 
                     halign='center',
                     valign='middle')
        min_width = max(len(self.text) * 15, 100)
        label.bind(
            texture_size=lambda lbl, size: setattr(self, 'width', max(size[0] + 40, min_width)))
        self.add_widget(label)

class TabbedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.bind(on_text_validate=self.on_enter)
        
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key, key_str = keycode
        if key == 9:  # Tab key
            self.focus_next()
            return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)
    
    def on_enter(self, instance):
        self.focus_next()
    
    def focus_next(self):
        # Obtener todos los inputs en la pestaña actual
        app = App.get_running_app()
        current_tab = app.tab_panel.current_tab
        inputs = []
        
        # Función recursiva para recolectar todos los TextInput
        def collect_inputs(widget):
            for child in widget.children:
                if isinstance(child, TextInput):
                    inputs.append(child)
                collect_inputs(child)
        
        collect_inputs(current_tab.content)
        
        if inputs:
            try:
                current_index = inputs.index(self)
                next_index = (current_index + 1) % len(inputs)
                next_input = inputs[next_index]
                Clock.schedule_once(lambda dt: setattr(next_input, 'focus', True), 0.1)
            except ValueError:
                # Si no encontramos el input actual en la lista, enfocar el primero
                if inputs:
                    Clock.schedule_once(lambda dt: setattr(inputs[0], 'focus', True), 0.1)
                    
class PasswordManagerApp(App):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        EventLoop.ensure_window()
        
        self.tab_panel = TabbedPanel(
            do_default_tab=False,
            tab_width=120,
            tab_height=40,
            background_color=(0.9, 0.9, 0.9, 1)
        )
        
        tabs = [
            ('Guardar', self.create_save_tab),
            ('Recuperar', self.create_recover_tab),
            ('Listar', self.create_list_tab),
            ('Eliminar', self.create_delete_tab)
        ]
        
        for text, creator in tabs:
            tab = creator()
            tab.text = text
            self.tab_panel.add_widget(tab)
            
        return self.tab_panel
    
    def on_request_close(self, *args):
        """Manejador mejorado para cerrar la aplicación"""
        try:
            # Cerrar todos los popups
            for child in Window.children[:]:
                if isinstance(child, Popup):
                    child.dismiss()
            
            # Detener la aplicación
            self.stop()
            
            # Cerrar la ventana
            if hasattr(Window, 'close'):
                Window.close()
            
            return True
        except Exception as e:
            print(f"Error al cerrar: {e}")
            import os
            os._exit(0)  # Fuerza el cierre si todo falla
        
    def create_save_tab(self):
        save_tab = CustomTabbedPanelItem()
        main_layout = BoxLayout(
            orientation='vertical', 
            padding=[10, Window.height * 0.1, 10, 10],  # Increased top padding to 10%
            spacing=10
        )
        
        # Title with bold formatting
        main_layout.add_widget(Label(text="Guardar Nueva Contraseña", size_hint_y=None, height=30, bold=True))
        
        # Save Password Section
        save_section = BoxLayout(orientation='vertical', spacing=10)
        save_section.add_widget(Label(text="Guardar Nueva Contraseña", size_hint_y=None, height=30, bold=True))
        
        # User field
        user_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        user_layout.add_widget(Label(text="Usuario:", size_hint_x=None, width=150))
        self.username_input = TabbedTextInput(hint_text="Usuario")
        user_layout.add_widget(self.username_input)
        save_section.add_widget(user_layout)
        
        # Site/App field
        site_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        site_layout.add_widget(Label(text="Sitio/Aplicación:", size_hint_x=None, width=150))
        self.site_input = TabbedTextInput(hint_text="Sitio/Aplicación")
        site_layout.add_widget(self.site_input)
        save_section.add_widget(site_layout)
        
        # Password field
        pass_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        pass_layout.add_widget(Label(text="Contraseña:", size_hint_x=None, width=150))
        self.password_input = TabbedTextInput(hint_text="Contraseña", password=True)
        pass_layout.add_widget(self.password_input)
        
        # Show password checkbox
        show_pass_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=150)
        show_pass_layout.add_widget(Label(text="Mostrar", size_hint_x=None, width=80))
        self.show_pass_checkbox = CheckBox(size_hint_x=None, width=30)
        self.show_pass_checkbox.bind(active=lambda checkbox, value: self.toggle_password_visibility(self.password_input, value))
        show_pass_layout.add_widget(self.show_pass_checkbox)
        pass_layout.add_widget(show_pass_layout)
        save_section.add_widget(pass_layout)
        
        # Add a name to the save button to make it easier to reference
        save_btn = Button(text="Guardar", size_hint_y=None, height=40, on_press=self.save_password)
        save_section.add_widget(save_btn)
    
        # Divider
        divider = Widget(size_hint_y=None, height=1)
        with divider.canvas:
            Color(0.5, 0.5, 0.5, 1)
            Rectangle(pos=divider.pos, size=(divider.width, 1))
        
        # Password Generator Section
        generator_section = BoxLayout(orientation='vertical', spacing=10)
        generator_section.add_widget(Label(text="Generador de Contraseñas", size_hint_y=None, height=30, bold=True))
        
        # Password length
        length_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        length_layout.add_widget(Label(text="Longitud:", size_hint_x=None, width=150))
        self.length_input = TabbedTextInput(text="16", multiline=False, size_hint_x=None, width=100)
        length_layout.add_widget(self.length_input)
        generator_section.add_widget(length_layout)
        
        # Checkboxes for password options
        options_layout = GridLayout(cols=4, size_hint_y=None, height=40)
        self.uppercase_check = CheckBox(active=True)
        options_layout.add_widget(Label(text="Mayúsculas"))
        options_layout.add_widget(self.uppercase_check)
        self.lowercase_check = CheckBox(active=True)
        options_layout.add_widget(Label(text="Minúsculas"))
        options_layout.add_widget(self.lowercase_check)
        self.numbers_check = CheckBox(active=True)
        options_layout.add_widget(Label(text="Números"))
        options_layout.add_widget(self.numbers_check)
        self.special_check = CheckBox(active=True)
        options_layout.add_widget(Label(text="Especiales"))
        options_layout.add_widget(self.special_check)
        generator_section.add_widget(options_layout)
        
        # Generate button
        generate_btn = Button(text="Generar", size_hint_y=None, height=40, on_press=self.generate_password)
        generator_section.add_widget(generate_btn)
        
        # Add sections to main layout
        main_layout.add_widget(save_section)
        main_layout.add_widget(divider)
        main_layout.add_widget(generator_section)
        save_tab.add_widget(main_layout)
        return save_tab
        
    def update_cred_display(self, instance, value):
        """Adjust the size of the credentials display label."""
        self.cred_display.size_hint_y = None
        self.cred_display.height = self.cred_display.texture_size[1]

    def create_recover_tab(self):
        recover_tab = CustomTabbedPanelItem(text='Recuperar Contraseña')
        recover_tab_layout = BoxLayout(
            orientation='vertical', 
            padding=[10, Window.height * 0.1, 10, 10],  # Consistent top padding
            spacing=10
        )

        # Title with bold formatting
        recover_tab_layout.add_widget(Label(text="Recuperar Contraseña", size_hint_y=None, height=30, bold=True))

        # User field
        user_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        user_layout.add_widget(Label(text="Usuario:", size_hint_x=None, width=150))
        self.rec_user_input = TabbedTextInput(hint_text="Usuario")
        user_layout.add_widget(self.rec_user_input)
        recover_tab_layout.add_widget(user_layout)

        # Site/App field
        site_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        site_layout.add_widget(Label(text="Sitio/Aplicación:", size_hint_x=None, width=150))
        self.rec_site_input = TabbedTextInput(hint_text="Sitio/Aplicación")
        site_layout.add_widget(self.rec_site_input)
        recover_tab_layout.add_widget(site_layout)

        # Admin password field
        admin_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        admin_layout.add_widget(Label(text="Contraseña Admin:", size_hint_x=None, width=150))
        self.admin_pass_input = TabbedTextInput(hint_text="Contraseña Admin", password=True)
        admin_layout.add_widget(self.admin_pass_input)
        
        # Show password checkbox
        show_pass_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=150)
        show_pass_layout.add_widget(Label(text="Mostrar", size_hint_x=None, width=80))
        self.rec_show_pass_checkbox = CheckBox(size_hint_x=None, width=30)
        self.rec_show_pass_checkbox.bind(active=lambda checkbox, value: self.toggle_password_visibility(self.admin_pass_input, value))
        show_pass_layout.add_widget(self.rec_show_pass_checkbox)
        admin_layout.add_widget(show_pass_layout)
        
        recover_tab_layout.add_widget(admin_layout)

        # Recover button
        recover_btn = Button(text="Recuperar", size_hint_y=None, height=40, on_press=self.retrieve_password)
        recover_tab_layout.add_widget(recover_btn)

        # Result label
        self.recover_result_label = Label(text="", size_hint_y=None, height=60)
        recover_tab_layout.add_widget(self.recover_result_label)

        recover_tab.add_widget(recover_tab_layout)
        return recover_tab

    def create_list_tab(self):
        list_tab = CustomTabbedPanelItem(text='Listar Credenciales')
        list_tab_layout = BoxLayout(
            orientation='vertical', 
            padding=[10, Window.height * 0.1, 10, 10],  # Consistent top padding
            spacing=10
        )

        # Title with bold formatting
        list_tab_layout.add_widget(Label(text="Listar Credenciales", size_hint_y=None, height=30, bold=True))

        # Admin password field
        admin_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        admin_layout.add_widget(Label(text="Contraseña Admin:", size_hint_x=None, width=150))
        self.list_admin_input = TabbedTextInput(hint_text="Contraseña Admin", password=True)
        admin_layout.add_widget(self.list_admin_input)
        
        # Show password checkbox
        show_pass_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=150)
        show_pass_layout.add_widget(Label(text="Mostrar", size_hint_x=None, width=80))
        self.list_show_pass_checkbox = CheckBox(size_hint_x=None, width=30)
        self.list_show_pass_checkbox.bind(active=lambda checkbox, value: self.toggle_password_visibility(self.list_admin_input, value))
        show_pass_layout.add_widget(self.list_show_pass_checkbox)
        admin_layout.add_widget(show_pass_layout)
        
        list_tab_layout.add_widget(admin_layout)

        # List button
        list_btn = Button(text="Mostrar Credenciales", size_hint_y=None, height=40, on_press=self.list_credentials)
        list_tab_layout.add_widget(list_btn)

        # ScrollView for credentials
        scroll_view = ScrollView(size_hint=(1, None), size=(Window.width - 40, 300), do_scroll_x=False)
        self.cred_display = Label(text="", size_hint_y=None, text_size=(Window.width - 60, None), halign='left', valign='top')
        self.cred_display.bind(texture_size=self.update_cred_display)
        scroll_view.add_widget(self.cred_display)
        list_tab_layout.add_widget(scroll_view)

        list_tab.add_widget(list_tab_layout)
        return list_tab

    def create_delete_tab(self):
        delete_tab = CustomTabbedPanelItem(text='Eliminar Credencial')
        delete_tab_layout = BoxLayout(
            orientation='vertical', 
            padding=[10, Window.height * 0.1, 10, 10],  # Consistent top padding
            spacing=10
        )

        # Title with bold formatting
        delete_tab_layout.add_widget(Label(text="Eliminar Credencial", size_hint_y=None, height=30, bold=True))

        # User field
        user_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        user_layout.add_widget(Label(text="Usuario:", size_hint_x=None, width=150))
        self.del_user_input = TabbedTextInput(hint_text="Usuario")
        user_layout.add_widget(self.del_user_input)
        delete_tab_layout.add_widget(user_layout)

        # Site/App field
        site_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        site_layout.add_widget(Label(text="Sitio/Aplicación:", size_hint_x=None, width=150))
        self.del_site_input = TabbedTextInput(hint_text="Sitio/Aplicación")
        site_layout.add_widget(self.del_site_input)
        delete_tab_layout.add_widget(site_layout)

        # Admin password field
        admin_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        admin_layout.add_widget(Label(text="Contraseña Admin:", size_hint_x=None, width=150))
        self.del_admin_input = TabbedTextInput(hint_text="Contraseña Admin", password=True)
        admin_layout.add_widget(self.del_admin_input)
            
        # Show password checkbox
        show_pass_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=150)
        show_pass_layout.add_widget(Label(text="Mostrar", size_hint_x=None, width=80))
        self.del_show_pass_checkbox = CheckBox(size_hint_x=None, width=30)
        self.del_show_pass_checkbox.bind(active=lambda checkbox, value: self.toggle_password_visibility(self.del_admin_input, value))
        show_pass_layout.add_widget(self.del_show_pass_checkbox)
        admin_layout.add_widget(show_pass_layout)
            
        delete_tab_layout.add_widget(admin_layout)

        # Delete button
        delete_btn = Button(text="Eliminar", size_hint_y=None, height=40, on_press=self.remove_password)
        delete_tab_layout.add_widget(delete_btn)
        
        # Result label
        self.delete_result_label = Label(text="", size_hint_y=None, height=60)
        delete_tab_layout.add_widget(self.delete_result_label)
        
        delete_tab.add_widget(delete_tab_layout)
        return delete_tab

    def toggle_password_visibility(self, entry, is_visible):
        """Toggle password visibility in the input field."""
        entry.password = not is_visible
        entry.text = entry.text  # Refresh the text display

    def generate_password(self, instance):
        """Generate a random password based on user preferences."""
        try:
            length = int(self.length_input.text)
            if length < 4 or length > 64:
                raise ValueError("Length must be between 4 and 64")
        except ValueError:
            self.show_popup("Error", "Longitud inválida. Debe ser un número entre 4 y 64")
            return

        use_upper = self.uppercase_check.active
        use_lower = self.lowercase_check.active
        use_numbers = self.numbers_check.active
        use_special = self.special_check.active

        if not any([use_upper, use_lower, use_numbers, use_special]):
            self.show_popup("Error", "Seleccione al menos un tipo de carácter")
            return

        password = generate_password(
            length=length,
            use_upper=use_upper,
            use_lower=use_lower,
            use_numbers=use_numbers,
            use_special=use_special
        )
        
        self.password_input.text = password
        self.password_input.password = False
        self.show_pass_checkbox.active = True

    def save_password(self, instance):
        username = self.username_input.text
        site = self.site_input.text
        password = self.password_input.text

        if not username or not site or not password:
            self.show_popup("Error", "Todos los campos son obligatorios")
            return

        if store_password(username, site, password):
            self.show_popup("Éxito", "Contraseña guardada con éxito")
            self.username_input.text = ""
            self.site_input.text = ""
            self.password_input.text = ""
        else:
            self.show_popup("Error", "Error al guardar la contraseña")

    def retrieve_password(self, instance):
        username = self.rec_user_input.text
        site = self.rec_site_input.text
        admin_password = self.admin_pass_input.text

        if not username or not site or not admin_password:
            self.show_popup("Error", "Ingrese usuario, sitio y contraseña de administrador")
            return

        if verify_admin_password(admin_password):
            stored_password = recover_password(username, site, admin_password)
            if stored_password:
                self.recover_result_label.text = f"Contraseña recuperada:\n{stored_password}"
            else:
                self.recover_result_label.text = "No se encontró la credencial"
        else:
            self.show_popup("Error", "Contraseña de administrador incorrecta")

    def list_credentials(self, instance):
        admin_password = self.list_admin_input.text

        if not admin_password:
            self.show_popup("Error", "Ingrese la contraseña de administrador")
            return

        if verify_admin_password(admin_password):
            credentials = list_credentials(admin_password)
            if credentials:
                cred_list = "\n".join([f"Usuario: {username}\nSitio: {site}\n" for username, site in credentials])
                self.cred_display.text = cred_list
            else:
                self.cred_display.text = "No hay credenciales almacenadas"
        else:
            self.show_popup("Error", "Contraseña de administrador incorrecta")

    def remove_password(self, instance):
        """Delete a stored credential"""
        username = self.del_user_input.text
        site = self.del_site_input.text
        admin_password = self.del_admin_input.text

        if not all([username, site, admin_password]):
            self.show_popup("Error", "Todos los campos son obligatorios")
            return

        if not verify_admin_password(admin_password):
            self.show_popup("Error", "Contraseña de administrador incorrecta")
            return

        if delete_password(username, site, admin_password):
            self.delete_result_label.text = "Credencial eliminada correctamente"
            self.del_user_input.text = ""
            self.del_site_input.text = ""
            self.del_admin_input.text = ""
        else:
            self.show_popup("Error", "No se pudo eliminar la credencial")

    def update_cred_display(self, instance, value):
        """Adjust the size of the credentials display label."""
        self.cred_display.size_hint_y = None
        self.cred_display.height = self.cred_display.texture_size[1]

    def show_popup(self, title, message, timeout=30):
        """Muestra un popup con botón de Aceptar que se cierra automáticamente después de timeout segundos"""
        content = BoxLayout(orientation='vertical', padding=10)
        message_label = Label(text=message)
        content.add_widget(message_label)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        
        btn = Button(text='Aceptar', size_hint=(1, 0.2))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        
        # Improved keyboard handling
        def on_key_down(window, keycode, *args):
            # Check if keycode is an integer or a tuple/list
            key = keycode if isinstance(keycode, int) else keycode[1] if isinstance(keycode, (tuple, list)) else None
            
            # Use Kivy's key name for Enter
            if key == 13 or (isinstance(key, str) and key.lower() == 'enter'):
                popup.dismiss()
                return True
            return False
        
        # Use Window.bind instead of popup.bind
        Window.bind(on_key_down=on_key_down)
        
        # Ensure the binding is removed after popup closes
        def cleanup_binding(popup_instance):
            Window.unbind(on_key_down=on_key_down)
        
        popup.bind(on_dismiss=cleanup_binding)
        
        # Mostrar el popup
        popup.open()
        
        # Programar el cierre automático después de 30 segundos
        Clock.schedule_once(lambda dt: popup.dismiss(), timeout)
        
if __name__ == '__main__':
    PasswordManagerApp().run()