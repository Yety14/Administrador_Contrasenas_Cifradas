from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from password_manager import store_password, recover_password, list_credentials

class PasswordManagerApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.username_input = TextInput(hint_text="Usuario", multiline=False)
        self.site_input = TextInput(hint_text="Sitio", multiline=False)
        self.password_input = TextInput(hint_text="Contraseña", multiline=False, password=True)
        
        save_btn = Button(text="Guardar Contraseña", on_press=self.save_password)
        retrieve_btn = Button(text="Recuperar Contraseña", on_press=self.retrieve_password)
        list_btn = Button(text="Listar Credenciales", on_press=self.list_credentials)

        self.result_label = Label(text="")

        layout.add_widget(self.username_input)
        layout.add_widget(self.site_input)
        layout.add_widget(self.password_input)
        layout.add_widget(save_btn)
        layout.add_widget(retrieve_btn)
        layout.add_widget(list_btn)
        layout.add_widget(self.result_label)

        return layout

    def save_password(self, instance):
        username = self.username_input.text
        site = self.site_input.text
        password = self.password_input.text

        if store_password(username, site, password):
            self.result_label.text = "✓ Contraseña guardada con éxito"
        else:
            self.result_label.text = "✗ Error: Ya existe una entrada"

    def retrieve_password(self, instance):
        self.result_label.text = "Función aún no implementada"

    def list_credentials(self, instance):
        self.result_label.text = "Función aún no implementada"

if __name__ == '__main__':
    PasswordManagerApp().run()
