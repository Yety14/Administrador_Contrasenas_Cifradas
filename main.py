from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from password_manager import (
    store_password, 
    recover_password, 
    list_credentials, 
    verify_admin_password,
    delete_password  # Asegúrate de que esta función esté implementada
)

class CustomTabbedPanelItem(TabbedPanelItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        label = Label(text=kwargs.get('text', ''), size_hint_x=None)
        label.bind(size=lambda *x: setattr(self, 'width', label.texture_size[0] + 20))  # Añadir padding
        self.add_widget(label)

class PasswordManagerApp(App):
    
    def build(self):
        self.tab_panel = TabbedPanel()

        # Pestaña para guardar contraseñas
        save_tab = CustomTabbedPanelItem(text='Guardar Contraseña')
        save_tab_layout = GridLayout(cols=3, padding=10, spacing=10)

        # Título de sección
        title_label = Label(text="Guardar Nueva Contraseña", size_hint_y=None, height=40)
        save_tab_layout.add_widget(title_label)

        # Campos de entrada
        fields = [
            ("👤 Usuario:", "username_input"),
            ("🌐 Sitio/Aplicación:", "site_input"),
            ("🔐 Contraseña:", "password_input", True)
        ]

        for i, (label_text, attr, *options) in enumerate(fields):
            label = Label(text=label_text, size_hint_x=None, width=150)
            save_tab_layout.add_widget(label)

            entry = TextInput(hint_text=label_text, multiline=False, password=True if options else False)
            setattr(self, attr, entry)
            save_tab_layout.add_widget(entry)

            # Checkbox para mostrar contraseña si es un campo de contraseña
            if options:
                show_pass_checkbox = CheckBox()
                show_pass_checkbox.bind(active=lambda checkbox, value: self.toggle_password_visibility(entry, value))
                save_tab_layout.add_widget(show_pass_checkbox)

        # Botón para guardar
        save_btn = Button(text="Guardar", on_press=self.save_password)
        save_tab_layout.add_widget(save_btn)

        # Etiqueta para mostrar resultados
        self.result_label = Label(text="", size_hint_y=None, height=40)
        save_tab_layout.add_widget(self.result_label)

        save_tab.add_widget(save_tab_layout)

        # Pestaña para recuperar contraseñas
        recover_tab = CustomTabbedPanelItem(text='Recuperar Contraseña')
        recover_tab_layout = GridLayout(cols=3, padding=10, spacing=10)

        # Título de sección
        recover_title_label = Label(text="Recuperar Contraseña", size_hint_y=None, height=40)
        recover_tab_layout.add_widget(recover_title_label)

        # Campos de entrada
        recover_fields = [
            ("👤 Usuario:", "rec_user_input"),
            ("🌐 Sitio/Aplicación:", "rec_site_input"),
            ("🔒 Contraseña Admin:", "admin_pass_input", True)
        ]

        for i, (label_text, attr, *options) in enumerate(recover_fields):
            label = Label(text=label_text, size_hint_x=None, width=150)
            recover_tab_layout.add_widget(label)

            entry = TextInput(hint_text=label_text, multiline=False, password=True if options else False)
            setattr(self, attr, entry)
            recover_tab_layout.add_widget(entry)

            # Checkbox para mostrar contraseña si es un campo de contraseña
            if options:
                show_pass_checkbox = CheckBox()
                show_pass_checkbox.bind(active=lambda checkbox, value: self.toggle_password_visibility(entry, value))
                recover_tab_layout.add_widget(show_pass_checkbox)

        # Botón para recuperar
        recover_btn = Button(text="🔍 Recuperar", on_press=self.retrieve_password)
        recover_tab_layout.add_widget(recover_btn)

        # Etiqueta para mostrar resultados
        self.recover_result_label = Label(text="", size_hint_y=None, height=40)
        recover_tab_layout.add_widget(self.recover_result_label)

        recover_tab.add_widget(recover_tab_layout)

        # Pestaña para listar credenciales
        list_tab = CustomTabbedPanelItem(text='Listar Credenciales')
        list_tab_layout = GridLayout(cols=3, padding=10, spacing=10)

        # Título de sección
        list_title_label = Label(text="Listar Credenciales", size_hint_y=None, height=40)
        list_tab_layout.add_widget(list_title_label)

        # Campo de entrada para la contraseña de administrador
        list_admin_label = Label(text="🔒 Contraseña Admin:", size_hint_x=None, width=150)
        list_tab_layout.add_widget(list_admin_label)

        self.list_admin_input = TextInput(hint_text="Contraseña Admin", multiline=False, password=True)
        list_tab_layout.add_widget(self.list_admin_input)

        # Checkbox para mostrar contraseña
        self.list_show_pass_checkbox = CheckBox()
        self.list_show_pass_checkbox.bind(active=lambda checkbox, value: self.toggle_password_visibility(self.list_admin_input, value))
        list_tab_layout.add_widget(self.list_show_pass_checkbox)

        # Botón para listar credenciales
        list_btn = Button(text="📋 Mostrar Credenciales", on_press=self.list_credentials)
        list_tab_layout.add_widget(list_btn)

        # ScrollView para mostrar las credenciales
        self.cred_display = Label(text="", size_hint_y=None)
        self.cred_display.bind(size=self.update_cred_display)
        scroll_view = ScrollView(size_hint=(1, None), size=(400, 200))
        scroll_view.add_widget(self.cred_display)
        list_tab_layout.add_widget(scroll_view)

        list_tab.add_widget(list_tab_layout)

        # Pestaña para eliminar credenciales
        delete_tab = CustomTabbedPanelItem(text='❌ Eliminar Credencial')
        delete_tab_layout = GridLayout(cols=3, padding=10, spacing=10)

        # Título de sección
        delete_title_label = Label(text="Eliminar Credencial", size_hint_y=None, height=40)
        delete_tab_layout.add_widget(delete_title_label)

        # Campos de entrada
        delete_fields = [
            ("👤 Usuario:", "del_user_input"),
            ("🌐 Sitio/Aplicación:", "del_site_input"),
            ("🔒 Contraseña Admin:", "del_admin_input", True)
        ]

        for i, (label_text, attr, *options) in enumerate(delete_fields):
            label = Label(text=label_text, size_hint_x=None, width=150)
            delete_tab_layout.add_widget(label)

            entry = TextInput(hint_text=label_text, multiline=False, password=True if options else False)
            setattr(self, attr, entry)
            delete_tab_layout.add_widget(entry)

            # Checkbox para mostrar contraseña si es un campo de contraseña
            if options:
                show_pass_checkbox = CheckBox()
                show_pass_checkbox.bind(active=lambda checkbox, value: self.toggle_password_visibility(entry, value))
                delete_tab_layout.add_widget(show_pass_checkbox)

        # Botón para eliminar
        delete_btn = Button(text="❌ Eliminar", on_press=self.remove_password)
        delete_tab_layout.add_widget(delete_btn)

        # Etiqueta para mostrar resultados
        self.delete_result_label = Label(text="", size_hint_y=None, height=40)
        delete_tab_layout.add_widget(self.delete_result_label)

        delete_tab.add_widget(delete_tab_layout)

        # Agregar pestañas al panel
        self.tab_panel.add_widget(save_tab)
        self.tab_panel.add_widget(recover_tab)
        self.tab_panel.add_widget(list_tab)
        self.tab_panel.add_widget(delete_tab)  # Agregar la pestaña de eliminar

        return self.tab_panel

    def toggle_password_visibility(self, entry, is_visible):
        """Alterna la visibilidad de la contraseña en el campo de entrada."""
        entry.password = not is_visible
        entry.text = entry.text  # Esto es necesario para actualizar el texto en el campo

    def save_password(self, instance):
        username = self.username_input.text
        site = self.site_input.text
        password = self.password_input.text

        if not username or not site or not password:
            self.show_popup("Error", "Todos los campos son obligatorios")
            return

        if store_password(username, site, password):
            self.result_label.text = "✓ Contraseña guardada con éxito"
        else:
            self.result_label.text = "✗ Error: Ya existe una entrada"

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
                self.recover_result_label.text = f"Contraseña recuperada: {stored_password}"
            else:
                self.recover_result_label.text = "✗ Error: No se encontró la credencial"
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
                cred_list = "\n".join([f"{username} - {site}" for username, site in credentials])
                self.cred_display.text = f"Credenciales:\n{cred_list}"
            else:
                self.cred_display.text = "✗ Error: No hay credenciales almacenadas"
        else:
            self.show_popup("Error", "Contraseña de administrador incorrecta")

    def remove_password(self, instance):
        """Elimina una credencial almacenada"""
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
            self.delete_result_label.text = "✓ Credencial eliminada correctamente"
            self.del_user_input.text = ""
            self.del_site_input.text = ""
            self.del_admin_input.text = ""
        else:
            self.show_popup("Error", "No se pudo eliminar la credencial")

    def update_cred_display(self, instance, value):
        """Ajusta el tamaño del Label que muestra las credenciales."""
        self.cred_display.size_hint_y = None
        self.cred_display.height = self.cred_display.texture_size[1]

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

if __name__ == '__main__':
    PasswordManagerApp().run()