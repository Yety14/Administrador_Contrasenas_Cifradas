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
from kivy.metrics import dp
from kivy.uix.spinner import Spinner
import random
from kivy.uix.floatlayout import FloatLayout
import string
import os
import sqlite3
import hashlib
import hmac
import base64
from kivy.config import Config
from cryptography.fernet import Fernet

# Configuración de paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWD_DIR = os.path.join(BASE_DIR, "passwd")
PASSWD_DB = os.path.join(PASSWD_DIR, "passwords.db")
SECRET_KEY_FILE = os.path.join(PASSWD_DIR, "secret.key")

# Configuración de seguridad
PBKDF2_ITERATIONS = 100000

def ensure_passwd_dir():
    """Crea el directorio seguro con permisos adecuados"""
    os.makedirs(PASSWD_DIR, exist_ok=True)
    if os.name == 'posix':
        os.chmod(PASSWD_DIR, 0o700)

def init_database(admin_password):
    """Inicializa la base de datos y archivos de seguridad"""
    ensure_passwd_dir()

    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    
    # Crear tablas
    c.execute('''CREATE TABLE IF NOT EXISTS credentials
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  site TEXT NOT NULL,
                  encrypted_password TEXT NOT NULL,
                  UNIQUE(username, site))''')

    c.execute('''CREATE TABLE IF NOT EXISTS admin
                 (id INTEGER PRIMARY KEY,
                  password_hash TEXT NOT NULL,
                  salt TEXT NOT NULL)''')
    
    # Si se proporciona una contraseña, guardarla
    if admin_password:
        salt = os.urandom(16)
        hashed_pw = hashlib.pbkdf2_hmac('sha256', admin_password.encode(), salt, PBKDF2_ITERATIONS)
        c.execute("INSERT OR REPLACE INTO admin VALUES (1, ?, ?)", 
                 (base64.b64encode(hashed_pw).decode(), base64.b64encode(salt).decode()))
    
    conn.commit()
    conn.close()
    os.chmod(PASSWD_DB, 0o600)

def get_cipher_key():
    """Genera o recupera la clave de cifrado"""
    ensure_passwd_dir()
    if os.path.exists(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = base64.urlsafe_b64encode(os.urandom(32))
        with open(SECRET_KEY_FILE, "wb") as f:
            f.write(key)
        os.chmod(SECRET_KEY_FILE, 0o600)
        return key

# Configuración de cifrado
KEY = get_cipher_key()
cipher_suite = Fernet(KEY)

def encrypt_password(password):
    """Cifra una contraseña"""
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    """Descifra una contraseña"""
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

def verify_admin_password(attempt):
    """Verifica la contraseña admin"""
    if not os.path.exists(PASSWD_DB):
        return False
        
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT password_hash, salt FROM admin WHERE id = 1")
    result = c.fetchone()
    conn.close()
    
    if not result:
        return False
        
    stored_hash = base64.b64decode(result[0].encode())
    salt = base64.b64decode(result[1].encode())
    attempt_hash = hashlib.pbkdf2_hmac('sha256', attempt.encode(), salt, PBKDF2_ITERATIONS)
    
    return hmac.compare_digest(stored_hash, attempt_hash)

def store_password(username, site, password):
    """Almacena una nueva contraseña o actualiza una existente"""
    encrypted_pw = encrypt_password(password)
    try:
        conn = sqlite3.connect(PASSWD_DB)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO credentials (username, site, encrypted_password) VALUES (?, ?, ?)",
                 (username, site, encrypted_pw))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error storing password: {e}")
        return False
    finally:
        conn.close()

def recover_password(username, site, admin_password):
    """Recupera una contraseña almacenada"""
    if not verify_admin_password(admin_password):
        return None
        
    try:
        conn = sqlite3.connect(PASSWD_DB)
        c = conn.cursor()
        c.execute("SELECT encrypted_password FROM credentials WHERE username = ? AND site = ?", (username, site))
        result = c.fetchone()
        return decrypt_password(result[0]) if result else None
    finally:
        conn.close()

def list_credentials(admin_password):
    """Lista todas las credenciales"""
    if not verify_admin_password(admin_password):
        return None
        
    try:
        conn = sqlite3.connect(PASSWD_DB)
        c = conn.cursor()
        c.execute("SELECT username, site FROM credentials ORDER BY username, site")
        return c.fetchall()
    finally:
        conn.close()

def delete_password(username, site, admin_password):
    """Elimina una credencial almacenada"""
    if not verify_admin_password(admin_password):
        return False
        
    try:
        conn = sqlite3.connect(PASSWD_DB)
        c = conn.cursor()
        c.execute("DELETE FROM credentials WHERE username = ? AND site = ?", (username, site))
        conn.commit()
        return c.rowcount > 0
    finally:
        conn.close()

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
        self.padding = [20, 5]
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
        self.is_last_field = kwargs.pop('is_last_field', False)
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
        if self.is_last_field:
            app = App.get_running_app()
            # Verificamos si estamos en el popup de configuración inicial
            if hasattr(app, 'setup_popup') and app.setup_popup:
                # En el popup de configuración, presionar Enter en el último campo activa el botón Aceptar
                for child in app.setup_popup.content.children:
                    if isinstance(child, BoxLayout):
                        for btn in child.children:
                            if isinstance(btn, Button) and btn.text == 'Aceptar':
                                btn.dispatch('on_press')
                                return
            else:
                # Comportamiento normal en las pestañas
                current_tab = app.tab_panel.current_tab.text if hasattr(app, 'tab_panel') else None
                if current_tab == 'Guardar':
                    app.save_password(None)
                elif current_tab == 'Recuperar':
                    app.retrieve_password(None)
                elif current_tab == 'Eliminar':
                    app.remove_password(None)
                elif current_tab == 'Listar':
                    app.list_credentials(None)
        else:
            self.focus_next()
    
    def focus_next(self):
        app = App.get_running_app()
        
        # Primero verificamos si estamos en el popup de configuración
        if hasattr(app, 'setup_popup') and app.setup_popup:
            if hasattr(app.setup_popup.content, 'tab_order'):
                try:
                    current_index = app.setup_popup.content.tab_order.index(self)
                    next_index = (current_index + 1) % len(app.setup_popup.content.tab_order)
                    next_widget = app.setup_popup.content.tab_order[next_index]
                    
                    if isinstance(next_widget, TextInput):
                        next_widget.focus = True
                    elif hasattr(next_widget, 'focus'):
                        next_widget.focus = True
                    return
                except ValueError:
                    pass
            return
        
        # Comportamiento normal en las pestañas
        if hasattr(app, 'tab_panel'):
            current_tab = app.tab_panel.current_tab
            if not current_tab or not current_tab.content:
                return
            
            if hasattr(current_tab, 'tab_order') and current_tab.tab_order:
                try:
                    current_index = current_tab.tab_order.index(self)
                    next_index = (current_index + 1) % len(current_tab.tab_order)
                    next_input = current_tab.tab_order[next_index]
                    Clock.schedule_once(lambda dt: setattr(next_input, 'focus', True), 0.1)
                except ValueError:
                    if current_tab.tab_order:
                        Clock.schedule_once(lambda dt: setattr(current_tab.tab_order[0], 'focus', True), 0.1)

class PasswordManagerApp(App):
    
    MIN_FONT_SIZE = 15
    DEFAULT_FONT_SIZE = 20
    MAX_FONT_SIZE = 25
    
    def build(self):
        # 1. Cargar configuración AL INICIO
        Config.read('config.ini')
        
        Window.bind(on_request_close=self.on_request_close)
        EventLoop.ensure_window()
        
        # Establecer tamaño de fuente desde configuración o por defecto
        self.font_size = Config.getint('ui', 'font_size', fallback=self.DEFAULT_FONT_SIZE)
        
        # Limitar el tamaño dentro de los rangos permitidos
        self.font_size = max(self.MIN_FONT_SIZE, min(self.font_size, self.MAX_FONT_SIZE))
        
        # 2. Verificar si es primera ejecución
        if not os.path.exists(PASSWD_DIR) or not os.path.exists(PASSWD_DB):
            self.show_admin_setup_popup()
            return Label(text="Por favor configure la contraseña de administrador")
        
        # 3. Crear interfaz principal
        root_layout = FloatLayout()
        self.tab_panel = self.create_main_interface()
        
        # 4. Añadir controles de zoom
        zoom_controls = BoxLayout(
            size_hint=(None, None), 
            size=(100, 40), 
            pos_hint={'right': 0.98, 'top': 0.98},
            spacing=5
        )
        
        btn_zoom_out = Button(text='-', size_hint_x=None, width=40)
        btn_zoom_in = Button(text='+', size_hint_x=None, width=40)
        
        btn_zoom_out.bind(on_press=self.zoom_out)
        btn_zoom_in.bind(on_press=self.zoom_in)
        
        zoom_controls.add_widget(btn_zoom_out)
        zoom_controls.add_widget(btn_zoom_in)
        
        # 5. Añadir feedback de tamaño actual
        self.zoom_feedback = Label(
            text=f"Tamaño: {self.font_size}px",
            size_hint=(None, None),
            size=(150, 30),
            pos_hint={'right': 0.95, 'top': 0.90},
            color=(0.2, 0.2, 0.2, 0.7)
        )
        
        # 6. Añadir todo al layout principal
        root_layout.add_widget(self.tab_panel)
        root_layout.add_widget(zoom_controls)
        root_layout.add_widget(self.zoom_feedback)
        
        # 7. Programar actualización de fuentes después de que la UI esté completamente cargada
        Clock.schedule_once(lambda dt: self.update_font_sizes(self.tab_panel), 0.1)
        
        return root_layout
    
    def on_key_down(self, window, key, *args):
        if key == 107 and 'ctrl' in args[3]:  # Ctrl++
            self.zoom_in(None)
        elif key == 109 and 'ctrl' in args[3]:  # Ctrl+-
            self.zoom_out(None)
        
    def update_font_sizes(self, root_widget=None):
        """Actualiza todos los textos de la interfaz con el tamaño actual"""
        if not hasattr(self, 'font_size'):
            return
            
        root = root_widget if root_widget is not None else self.root
        if root is None:
            return
        
        # Actualizar widgets principales
        for widget in root.walk():
            if isinstance(widget, (Label, Button, TextInput, Spinner)):
                widget.font_size = self.font_size
            
            # Tamaño especial para pestañas
            if isinstance(widget, TabbedPanelItem):
                for child in widget.children:
                    if isinstance(child, Label):
                        child.font_size = max(self.font_size - 2, 12)
        
        # Actualizar feedback de zoom
        if hasattr(self, 'zoom_feedback'):
            self.zoom_feedback.text = f"Tamaño: {self.font_size}px"
        
        # Actualizar popups abiertos si existen
        for child in Window.children:
            if isinstance(child, Popup):
                for popup_widget in child.content.walk():
                    if isinstance(popup_widget, (Label, Button, TextInput)):
                        popup_widget.font_size = self.font_size

    def zoom_out(self, instance):
        self.font_size = max(self.font_size - 1, self.MIN_FONT_SIZE)
        self.update_font_sizes(self.tab_panel)
        self.save_font_size()

    def zoom_in(self, instance):
        self.font_size = min(self.font_size + 1, self.MAX_FONT_SIZE)
        self.update_font_sizes(self.tab_panel)
        self.save_font_size()
        
    def save_font_size(self):
        """Guarda el tamaño de fuente actual en la configuración"""
        from kivy.config import Config
        try:
            if not Config.has_section('ui'):
                Config.add_section('ui')
            Config.set('ui', 'font_size', str(self.font_size))
            Config.write()
        except Exception as e:
            print(f"Error guardando tamaño de fuente: {e}")
            
    def on_request_close(self, *args):
        """Manejador para cerrar la aplicación correctamente"""
        try:
            # 1. Guardar configuración actual primero
            self.save_font_size()
            
            # 2. Cerrar todos los popups abiertos
            for child in Window.children[:]:
                if isinstance(child, Popup):
                    child.dismiss()
            
            # 3. Detener la aplicación
            self.stop()
            
            # 4. Forzar cierre de la ventana si es necesario
            if hasattr(Window, 'close'):
                Window.close()
            
            # 5. En algunos sistemas es necesario esto
            import os
            os._exit(0)
            
            return True
        except Exception as e:
            print(f"Error al cerrar: {e}")
            import os
            os._exit(1)
    
    def show_admin_setup_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        lbl = Label(text="Configuración Inicial\nEstablezca la contraseña de administrador", 
                   halign='center', font_size=16)
        content.add_widget(lbl)
        
        self.setup_pass1 = TabbedTextInput(
            hint_text="Contraseña", 
            password=True, 
            size_hint_y=None, 
            height=40,
            is_last_field=False
        )
        content.add_widget(self.setup_pass1)
        
        self.setup_pass2 = TabbedTextInput(
            hint_text="Confirmar contraseña", 
            password=True, 
            size_hint_y=None, 
            height=40,
            is_last_field=True
        )
        content.add_widget(self.setup_pass2)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_cancel = Button(text="Cancelar")
        btn_accept = Button(text="Aceptar")
        
        # Hacemos que los botones puedan recibir foco
        btn_cancel.focusable = True
        btn_accept.focusable = True
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_accept)
        content.add_widget(btn_layout)
        
        # Establecemos el orden de tabulación
        content.tab_order = [self.setup_pass1, self.setup_pass2, btn_cancel, btn_accept]
        
        self.setup_popup = Popup(
            title="Configuración Inicial", 
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        def setup_admin(instance):
            if not self.setup_pass1.text or not self.setup_pass2.text:
                lbl.text = "Error: Ambas contraseñas son requeridas"
                lbl.color = (1, 0, 0, 1)
                return
                
            if self.setup_pass1.text != self.setup_pass2.text:
                lbl.text = "Error: Las contraseñas no coinciden"
                lbl.color = (1, 0, 0, 1)
                return
                
            try:
                init_database(self.setup_pass1.text)
                self.setup_popup.dismiss()
                Window.remove_widget(Window.children[0])
                Window.add_widget(self.create_main_interface())
            except Exception as e:
                lbl.text = f"Error en configuración: {str(e)}"
                lbl.color = (1, 0, 0, 1)
        
        def cancel_setup(instance):
            # Eliminamos la carpeta passwd si existe
            try:
                if os.path.exists(PASSWD_DIR):
                    import shutil
                    shutil.rmtree(PASSWD_DIR)
            except Exception as e:
                print(f"Error al eliminar directorio: {e}")
            
            # Cerramos la aplicación
            self.setup_popup.dismiss()
            self.stop()
        
        btn_accept.bind(on_press=setup_admin)
        btn_cancel.bind(on_press=cancel_setup)
        
        # Configuramos el foco inicial
        Clock.schedule_once(lambda dt: setattr(self.setup_pass1, 'focus', True), 0.1)
        
        self.setup_popup.open()    
    
    def create_main_interface(self):
        """Crea la interfaz principal de pestañas"""
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
        
        self.tab_panel.bind(current_tab=self.on_tab_changed)
        return self.tab_panel
    
    def on_tab_changed(self, instance, value):
        Clock.schedule_once(lambda dt: self.focus_first_input(), 0.1)
    
    def focus_first_input(self):
        current_tab = self.tab_panel.current_tab
        if not current_tab or not current_tab.content:
            return
        
        if hasattr(current_tab, 'tab_order') and current_tab.tab_order:
            current_tab.tab_order[0].focus = True
    
    def create_save_tab(self):
        save_tab = CustomTabbedPanelItem()
        main_layout = BoxLayout(
            orientation='vertical', 
            padding=[10, Window.height * 0.1, 10, 10],
            spacing=10
        )
        
        # Title
        main_layout.add_widget(Label(text="Guardar Nueva Contraseña", size_hint_y=None, height=30, bold=True))
        
        # Save Password Section
        save_section = BoxLayout(orientation='vertical', spacing=10)
        
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
        self.password_input = TabbedTextInput(hint_text="Contraseña", password=True, is_last_field=True)
        pass_layout.add_widget(self.password_input)
        
        # Show password checkbox
        show_pass_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=150)
        show_pass_layout.add_widget(Label(text="Mostrar", size_hint_x=None, width=80))
        self.show_pass_checkbox = CheckBox(size_hint_x=None, width=30)
        self.show_pass_checkbox.bind(active=lambda checkbox, value: self.toggle_password_visibility(self.password_input, value))
        show_pass_layout.add_widget(self.show_pass_checkbox)
        pass_layout.add_widget(show_pass_layout)
        save_section.add_widget(pass_layout)
        
        # Save button
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
        
        # Password length spinner
        length_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        length_layout.add_widget(Label(text="Longitud:", size_hint_x=None, width=150))
        self.length_spinner = Spinner(
            text='16',
            values=[str(i) for i in range(8, 33)],
            size_hint_x=None,
            width=100
        )
        length_layout.add_widget(self.length_spinner)
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
        
        # Set tab order for this tab
        save_tab.tab_order = [self.username_input, self.site_input, self.password_input]
        
        save_tab.add_widget(main_layout)
        return save_tab
        
    def create_recover_tab(self):
        recover_tab = CustomTabbedPanelItem(text='Recuperar Contraseña')
        recover_tab_layout = BoxLayout(
            orientation='vertical', 
            padding=[10, Window.height * 0.1, 10, 10],
            spacing=10
        )

        # Title
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
        self.admin_pass_input = TabbedTextInput(hint_text="Contraseña Admin", password=True, is_last_field=True)
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

        # Set tab order for this tab
        recover_tab.tab_order = [self.rec_user_input, self.rec_site_input, self.admin_pass_input]

        recover_tab.add_widget(recover_tab_layout)
        return recover_tab

    def create_list_tab(self):
        list_tab = CustomTabbedPanelItem(text='Listar Credenciales')
        list_tab_layout = BoxLayout(
            orientation='vertical', 
            padding=[10, Window.height * 0.1, 10, 10],
            spacing=10
        )

        # Title
        list_tab_layout.add_widget(Label(text="Listar Credenciales", size_hint_y=None, height=30, bold=True))

        # Admin password field
        admin_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        admin_layout.add_widget(Label(text="Contraseña Admin:", size_hint_x=None, width=150))
        self.list_admin_input = TabbedTextInput(hint_text="Contraseña Admin", password=True,is_last_field=True)
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

        # Set tab order for this tab
        list_tab.tab_order = [self.list_admin_input]

        list_tab.add_widget(list_tab_layout)
        return list_tab

    def create_delete_tab(self):
        delete_tab = CustomTabbedPanelItem(text='Eliminar Credencial')
        delete_tab_layout = BoxLayout(
            orientation='vertical', 
            padding=[10, Window.height * 0.1, 10, 10],
            spacing=10
        )

        # Title
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
        self.del_admin_input = TabbedTextInput(hint_text="Contraseña Admin", password=True, is_last_field=True)
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
        
        # Set tab order for this tab
        delete_tab.tab_order = [self.del_user_input, self.del_site_input, self.del_admin_input]
        
        delete_tab.add_widget(delete_tab_layout)
        return delete_tab

    def toggle_password_visibility(self, entry, is_visible):
        """Toggle password visibility in the input field."""
        entry.password = not is_visible
        entry.text = entry.text  # Refresh the text display

    def generate_password(self, instance):
        """Generate a random password based on user preferences."""
        try:
            length = int(self.length_spinner.text)
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

        # Función para guardar/actualizar después de confirmación
        def perform_save(overwrite=False):
            try:
                if store_password(username, site, password):
                    message = "Contraseña guardada correctamente" if not overwrite else "Contraseña actualizada correctamente"
                    self.show_popup("Éxito", message)
                    self.clear_fields()
                else:
                    self.show_popup("Error", "No se pudo guardar la contraseña")
            except Exception as e:
                self.show_popup("Error", f"Error inesperado: {str(e)}")

        # Verificar si ya existe
        try:
            with sqlite3.connect(PASSWD_DB) as conn:
                c = conn.cursor()
                c.execute("""SELECT 1 FROM credentials 
                            WHERE username = ? AND site = ?""",
                         (username, site))
                exists = c.fetchone() is not None

            if exists:
                # Mostrar popup de confirmación
                content = BoxLayout(orientation='vertical', spacing=10, padding=10)
                content.add_widget(Label(
                    text=f"Ya existe una contraseña para:\nUsuario: {username}\nSitio: {site}",
                    halign='center'
                ))
                content.add_widget(Label(
                    text="¿Desea actualizarla?",
                    bold=True,
                    color=(1, 0.5, 0, 1)  # Color naranja
                ))

                btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
                btn_si = Button(text="Sí, actualizar")
                btn_no = Button(text="No, cancelar")
                
                btn_si.bind(on_press=lambda x: (popup.dismiss(), perform_save(True)))
                btn_no.bind(on_press=popup.dismiss)
                
                btn_layout.add_widget(btn_no)
                btn_layout.add_widget(btn_si)
                content.add_widget(btn_layout)

                popup = Popup(title="Confirmar actualización",
                             content=content,
                             size_hint=(0.8, 0.4))
                popup.open()
            else:
                perform_save()

        except Exception as e:
            self.show_popup("Error", f"Error al verificar credenciales: {str(e)}")

    def clear_fields(self):
        """Limpia los campos del formulario"""
        self.username_input.text = ""
        self.site_input.text = ""
        self.password_input.text = ""
        
    def retrieve_password(self, instance):
        username = self.rec_user_input.text
        site = self.rec_site_input.text
        admin_password = self.admin_pass_input.text

        if not username or not site or not admin_password:
            self.show_popup("Error", "Ingrese usuario, sitio y contraseña de administrador")
            return

        stored_password = recover_password(username, site, admin_password)
        if stored_password:
            self.recover_result_label.text = f"Contraseña recuperada:\n{stored_password}"
        else:
            self.recover_result_label.text = "No se encontró la credencial o contraseña admin incorrecta"

    def list_credentials(self, instance):
        admin_password = self.list_admin_input.text

        if not admin_password:
            self.show_popup("Error", "Ingrese la contraseña de administrador")
            return

        credentials = list_credentials(admin_password)
        if credentials is None:
            self.show_popup("Error", "Contraseña de administrador incorrecta")
            return
            
        if credentials:
            cred_list = "\n".join([f"Usuario: {username}\nSitio: {site}\n" for username, site in credentials])
            self.cred_display.text = cred_list
        else:
            self.cred_display.text = "No hay credenciales almacenadas"

    def remove_password(self, instance):
        """Delete a stored credential"""
        username = self.del_user_input.text
        site = self.del_site_input.text
        admin_password = self.del_admin_input.text

        if not all([username, site, admin_password]):
            self.show_popup("Error", "Todos los campos son obligatorios")
            return

        if delete_password(username, site, admin_password):
            self.delete_result_label.text = "Credencial eliminada correctamente"
            self.del_user_input.text = ""
            self.del_site_input.text = ""
            self.del_admin_input.text = ""
        else:
            self.delete_result_label.text = "No se pudo eliminar la credencial o contraseña admin incorrecta"

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
        
        def on_key_down(window, keycode, *args):
            key = keycode if isinstance(keycode, int) else keycode[1] if isinstance(keycode, (tuple, list)) else None
            
            if key == 13 or (isinstance(key, str) and key.lower() == 'enter'):
                popup.dismiss()
                return True
            return False
        
        Window.bind(on_key_down=on_key_down)
        
        def cleanup_binding(popup_instance):
            Window.unbind(on_key_down=on_key_down)
        
        popup.bind(on_dismiss=cleanup_binding)
        
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), timeout)

if __name__ == '__main__':
    PasswordManagerApp().run()