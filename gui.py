import os
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, font
import sqlite3
from datetime import datetime

from password_manager import (
    ensure_passwd_dir, 
    init_database, 
    verify_admin_password,
    store_password, 
    recover_password, 
    delete_password, 
    list_credentials,
    check_duplicate,
    update_password,
    PASSWD_DB,
    MAX_LOGIN_ATTEMPTS,
    LOCKOUT_TIME
)

class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Contraseñas Seguro")
        self.root.geometry("900x700")
        
        # Configuraciones de tema y personalización
        self.current_theme = tk.StringVar(value="light")
        self.font_size = tk.IntVar(value=10)
        
        self.configure_styles()
        self.setup_ui()
        self.setup_theme_menu()
        
        if not os.path.exists(PASSWD_DB):
            self.setup_admin_password()

    def configure_styles(self):
        """Configura estilos con soporte para temas claro y oscuro"""
        style = ttk.Style()
        style.theme_use('clam')

        # Definir paletas de colores
        self.themes = {
            "light": {
                "bg_color": '#f0f0f0',
                "fg_color": '#2c3e50',
                "primary_color": '#3498db',
                "secondary_color": '#2ecc71',
                "text_color": '#2c3e50',
                "entry_bg": 'white',
                "entry_fg": 'black',
                "frame_bg": '#f0f0f0',
                "button_bg": '#3498db',
                "button_fg": 'white',
                "tree_bg": 'white',
                "tree_fg": 'black',
                "tree_heading_bg": '#3498db',
                "tree_heading_fg": 'white'
            },
            "dark": {
                "bg_color": '#2c3e50',
                "fg_color": '#ecf0f1',
                "primary_color": '#34495e',
                "secondary_color": '#27ae60',
                "text_color": '#ecf0f1',
                "entry_bg": '#34495e',
                "entry_fg": 'white',
                "frame_bg": '#34495e',
                "button_bg": '#2980b9',
                "button_fg": 'white',
                "tree_bg": '#34495e',
                "tree_fg": 'white',
                "tree_heading_bg": '#2980b9',
                "tree_heading_fg": 'white'
            }
        }

        # Aplicar tema inicial
        self.apply_theme()

    def apply_theme(self, theme=None):
        """Aplica el tema seleccionado a todos los widgets"""
        if theme:
            self.current_theme.set(theme)
        
        current_theme = self.themes[self.current_theme.get()]
        style = ttk.Style()

        # Configurar colores base
        self.root.configure(bg=current_theme['bg_color'])
        
        # Configurar estilo de los widgets ttk
        style.configure('.', 
                      background=current_theme['bg_color'],
                      foreground=current_theme['fg_color'],
                      font=('Arial', self.font_size.get()))
        
        style.configure('TFrame', background=current_theme['frame_bg'])
        style.configure('TLabel', 
                       background=current_theme['frame_bg'],
                       foreground=current_theme['text_color'])
        style.configure('TButton', 
                       background=current_theme['button_bg'],
                       foreground=current_theme['button_fg'],
                       font=('Arial', self.font_size.get(), 'bold'))
        style.configure('TEntry',
                       fieldbackground=current_theme['entry_bg'],
                       foreground=current_theme['entry_fg'])
        style.configure('TCheckbutton',
                       background=current_theme['frame_bg'],
                       foreground=current_theme['text_color'])
        
        # Configurar Notebook
        style.configure('TNotebook', background=current_theme['bg_color'])
        style.map('TNotebook.Tab', 
                 background=[('selected', current_theme['primary_color']), 
                            ('!selected', current_theme['bg_color'])],
                 foreground=[('selected', 'white'), 
                            ('!selected', current_theme['text_color'])])
        
        # Configurar Treeview
        style.configure('Treeview',
                      background=current_theme['tree_bg'],
                      foreground=current_theme['tree_fg'],
                      fieldbackground=current_theme['tree_bg'])
        style.configure('Treeview.Heading',
                      background=current_theme['tree_heading_bg'],
                      foreground=current_theme['tree_heading_fg'])
        
        # Actualizar todos los widgets
        self.update_widget_colors()

    def update_widget_colors(self):
        """Actualiza manualmente los colores de los widgets que no son ttk"""
        current_theme = self.themes[self.current_theme.get()]
        
        # Recorrer todos los widgets y actualizar sus colores
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=current_theme['frame_bg'])
            elif isinstance(widget, tk.Label):
                widget.configure(bg=current_theme['frame_bg'], fg=current_theme['text_color'])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=current_theme['entry_bg'], fg=current_theme['entry_fg'],
                               insertbackground=current_theme['entry_fg'])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=current_theme['button_bg'], fg=current_theme['button_fg'])
            elif isinstance(widget, tk.Checkbutton):
                widget.configure(bg=current_theme['frame_bg'], fg=current_theme['text_color'])
            
            # Actualizar también los hijos de los widgets
            for child in widget.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=current_theme['frame_bg'])
                elif isinstance(child, tk.Label):
                    child.configure(bg=current_theme['frame_bg'], fg=current_theme['text_color'])
                elif isinstance(child, tk.Entry):
                    child.configure(bg=current_theme['entry_bg'], fg=current_theme['entry_fg'],
                                   insertbackground=current_theme['entry_fg'])
                elif isinstance(child, tk.Button):
                    child.configure(bg=current_theme['button_bg'], fg=current_theme['button_fg'])
                elif isinstance(child, tk.Checkbutton):
                    child.configure(bg=current_theme['frame_bg'], fg=current_theme['text_color'])

    def setup_theme_menu(self):
        """Crea un menú para personalización con botones de zoom"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Menú de Ver
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Ver", menu=view_menu)

        # Submenú de temas
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Tema", menu=theme_menu)
        theme_menu.add_radiobutton(label="Claro", command=lambda: self.apply_theme("light"))
        theme_menu.add_radiobutton(label="Oscuro", command=lambda: self.apply_theme("dark"))

        # Botones de zoom
        view_menu.add_command(label="Ampliar (Ctrl+)", command=self.zoom_in)
        view_menu.add_command(label="Alejar (Ctrl-)", command=self.zoom_out)

        # Botón de maximizar/restaurar
        view_menu.add_separator()
        view_menu.add_command(label="Maximizar/Restaurar", command=self.toggle_window_size)

        # Atajos de teclado
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-equal>", lambda e: self.zoom_in())  # Para teclados sin + independiente

    def zoom_in(self):
        """Aumenta el tamaño de fuente"""
        if self.font_size.get() < 20:  # Límite máximo
            self.font_size.set(self.font_size.get() + 1)
            self.apply_theme()
            self.setup_ui()

    def zoom_out(self):
        """Reduce el tamaño de fuente"""
        if self.font_size.get() > 8:  # Límite mínimo
            self.font_size.set(self.font_size.get() - 1)
            self.apply_theme()
            self.setup_ui()
            
    def update_font_size(self, size):
        """Actualiza el tamaño de fuente"""
        self.font_size.set(size)
        self.apply_theme()
        # Forzar refresco de ventanas
        self.setup_ui()

    def toggle_window_size(self):
        """Alterna entre ventana maximizada y restaurada"""
        if self.root.state() == 'zoomed':
            self.root.state('normal')
        else:
            self.root.state('zoomed')

    def setup_ui(self):
        """Configura la interfaz de usuario principal con un diseño mejorado"""
        # Frame principal con un poco de padding
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook con apariencia moderna
        self.notebook = ttk.Notebook(main_frame, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Crear pestañas con un diseño más atractivo
        self.create_save_tab()
        self.create_recover_tab()
        self.create_list_tab()
        self.create_delete_tab()

    def setup_admin_password(self):
        """Configura la contraseña de administrador inicial"""
        password = simpledialog.askstring(
            "Configuración inicial",
            "Establezca la contraseña de administrador:",
            show='*'
        )
        if password:
            init_database(password)
            messagebox.showinfo("Éxito", "Configuración completada exitosamente")
        else:
            messagebox.showerror("Error", "Debe establecer una contraseña de administrador")
            self.root.destroy()

    def create_save_tab(self):
        """Pestaña para guardar/actualizar contraseñas con diseño mejorado"""
        tab = ttk.Frame(self.notebook, padding="20 20 20 20")
        self.notebook.add(tab, text=" 💾 Guardar/Actualizar ")

        # Título de sección
        ttk.Label(tab, text="Guardar Nueva Contraseña", 
                  font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=3, pady=(0,20))

        # Campos de entrada
        fields = [
            ("👤 Usuario:", "user_entry"),
            ("🌐 Sitio/Aplicación:", "site_entry"),
            ("🔐 Contraseña:", "pass_entry", True)
        ]
        
        for i, (label, attr, *options) in enumerate(fields, start=1):
            ttk.Label(tab, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(tab, show="*" if options else "", width=40)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            setattr(self, attr, entry)
            
            # Añadir checkbox para mostrar contraseña si es un campo de contraseña
            if options:
                show_pass_var = tk.BooleanVar(value=False)
                show_pass_check = ttk.Checkbutton(tab, text="Mostrar", 
                                               variable=show_pass_var,
                                               command=lambda e=entry, v=show_pass_var: self.toggle_single_password(e, v))
                show_pass_check.grid(row=i, column=2, padx=5, pady=5, sticky="w")
            
            tab.columnconfigure(1, weight=1)

        # Botón de guardar con estilo
        save_btn = ttk.Button(tab, text="💾 Guardar", command=self.save_password)
        save_btn.grid(row=len(fields)+1, column=0, columnspan=3, pady=20)
        
        self.pass_entry.bind("<Return>", lambda event: self.save_password())

    def create_recover_tab(self):
        """Pestaña para recuperar contraseñas con diseño mejorado"""
        tab = ttk.Frame(self.notebook, padding="20 20 20 20")
        self.notebook.add(tab, text=" 🔍 Recuperar ")

        # Título de sección
        ttk.Label(tab, text="Recuperar Contraseña", 
                  font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=3, pady=(0,20))

        # Campos de entrada
        fields = [
            ("👤 Usuario:", "rec_user_entry"),
            ("🌐 Sitio/Aplicación:", "rec_site_entry"),
            ("🔒 Contraseña Admin:", "admin_pass_entry", True)
        ]
        
        for i, (label, attr, *options) in enumerate(fields, start=1):
            ttk.Label(tab, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(tab, show="*" if options else "", width=40)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            setattr(self, attr, entry)
            
            # Añadir checkbox para mostrar contraseña si es un campo de contraseña
            if options:
                show_pass_var = tk.BooleanVar(value=False)
                show_pass_check = ttk.Checkbutton(tab, text="Mostrar", 
                                               variable=show_pass_var,
                                               command=lambda e=entry, v=show_pass_var: self.toggle_single_password(e, v))
                show_pass_check.grid(row=i, column=2, padx=5, pady=5, sticky="w")
            
            tab.columnconfigure(1, weight=1)

        # Resultado - Usamos un Label directo en lugar de StringVar para evitar el punto blanco
        self.result_label = ttk.Label(tab, text="", wraplength=300)
        self.result_label.grid(row=len(fields)+1, column=0, columnspan=3, pady=10)

        recover_btn = ttk.Button(tab, text="🔍 Recuperar", command=self.recover_password)
        recover_btn.grid(row=len(fields)+2, column=0, columnspan=3, pady=20)
        
        self.admin_pass_entry.bind("<Return>", lambda event: self.recover_password())

    def create_list_tab(self):
        """Pestaña para listar credenciales con diseño mejorado"""
        tab = ttk.Frame(self.notebook, padding="20 20 20 20")
        self.notebook.add(tab, text=" 📋 Listar ")

        # Título de sección
        ttk.Label(tab, text="Listar Credenciales", 
                  font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=3, pady=(0,20))

        ttk.Label(tab, text="🔒 Contraseña Admin:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.list_admin_entry = ttk.Entry(tab, show="*", width=40)
        self.list_admin_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Checkbox para mostrar contraseña
        self.list_show_pass_var = tk.BooleanVar(value=False)
        show_pass_check = ttk.Checkbutton(tab, text="Mostrar", 
                                        variable=self.list_show_pass_var,
                                        command=lambda: self.toggle_single_password(self.list_admin_entry, self.list_show_pass_var))
        show_pass_check.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Treeview con estilo mejorado
        self.tree = ttk.Treeview(tab, columns=("Usuario", "Sitio"), show="headings", height=10)
        self.tree.heading("Usuario", text="👤 Usuario")
        self.tree.heading("Sitio", text="🌐 Sitio/Aplicación")
        self.tree.column("Usuario", width=200)
        self.tree.column("Sitio", width=300)
        self.tree.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=2, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        list_btn = ttk.Button(tab, text="📋 Mostrar Credenciales", command=self.list_passwords)
        list_btn.grid(row=3, column=0, columnspan=3, pady=20)

        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(2, weight=1)
        self.list_admin_entry.bind("<Return>", lambda event: self.list_passwords())

    def create_delete_tab(self):
        """Pestaña para eliminar credenciales con diseño mejorado"""
        tab = ttk.Frame(self.notebook, padding="20 20 20 20")
        self.notebook.add(tab, text=" ❌ Eliminar ")

        # Título de sección
        ttk.Label(tab, text="Eliminar Credencial", 
                  font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=3, pady=(0,20))

        # Campos de entrada
        fields = [
            ("👤 Usuario:", "del_user_entry"),
            ("🌐 Sitio/Aplicación:", "del_site_entry"),
            ("🔒 Contraseña Admin:", "del_admin_entry", True)
        ]
        
        for i, (label, attr, *options) in enumerate(fields, start=1):
            ttk.Label(tab, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(tab, show="*" if options else "", width=40)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            setattr(self, attr, entry)
            
            # Añadir checkbox para mostrar contraseña si es un campo de contraseña
            if options:
                show_pass_var = tk.BooleanVar(value=False)
                show_pass_check = ttk.Checkbutton(tab, text="Mostrar", 
                                               variable=show_pass_var,
                                               command=lambda e=entry, v=show_pass_var: self.toggle_single_password(e, v))
                show_pass_check.grid(row=i, column=2, padx=5, pady=5, sticky="w")
            
            tab.columnconfigure(1, weight=1)

        delete_btn = ttk.Button(tab, text="❌ Eliminar", command=self.remove_password)
        delete_btn.grid(row=len(fields)+1, column=0, columnspan=3, pady=20)
        
        self.del_admin_entry.bind("<Return>", lambda event: self.remove_password())

    def toggle_single_password(self, entry_widget, show_var):
        """Alterna la visibilidad de una contraseña específica"""
        entry_widget.configure(show="" if show_var.get() else "*")

    def verify_admin_password_gui(self, attempt):
        """Versión adaptada para GUI con manejo de bloqueos"""
        if not verify_admin_password(attempt):
            conn = sqlite3.connect(PASSWD_DB)
            c = conn.cursor()
            c.execute("SELECT attempts, locked_until FROM login_attempts WHERE id = 1")
            attempts, locked_until = c.fetchone()
            conn.close()
            
            if locked_until and datetime.now() < datetime.fromisoformat(locked_until):
                remaining = (datetime.fromisoformat(locked_until) - datetime.now()).seconds
                messagebox.showerror(
                    "Cuenta bloqueada",
                    f"Demasiados intentos fallidos. Espere {remaining} segundos"
                )
                return False
            
            remaining_attempts = MAX_LOGIN_ATTEMPTS - attempts
            messagebox.showerror(
                "Error",
                f"Contraseña incorrecta. Intentos restantes: {remaining_attempts}"
            )
            return False
        return True

    def save_password(self):
        """Guarda o actualiza una contraseña"""
        username = self.user_entry.get()
        site = self.site_entry.get()
        password = self.pass_entry.get()

        if not all([username, site, password]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        if check_duplicate(username, site):
            self.handle_duplicate_password(username, site, password)
        else:
            if store_password(username, site, password):
                messagebox.showinfo("Éxito", "Contraseña guardada correctamente")
                self.clear_entries()

    def handle_duplicate_password(self, username, site, new_password):
        """Maneja la actualización de contraseñas existentes"""
        if messagebox.askyesno("Confirmar", "Ya existe una entrada. ¿Desea actualizar?"):
            admin_pw = simpledialog.askstring("Admin", "Ingrese contraseña de administrador:", show='*')
            if admin_pw and self.verify_admin_password_gui(admin_pw):
                if update_password(username, site, new_password):
                    messagebox.showinfo("Éxito", "Contraseña actualizada")
                    self.clear_entries()

    def recover_password(self):
        """Recupera una contraseña almacenada"""
        username = self.rec_user_entry.get()
        site = self.rec_site_entry.get()
        admin_pw = self.admin_pass_entry.get()

        if not all([username, site, admin_pw]):
            self.result_label.config(text="Error: Todos los campos son obligatorios")
            return

        if not self.verify_admin_password_gui(admin_pw):
            self.result_label.config(text="Error: Contraseña de administrador incorrecta")
            return

        stored_password = recover_password(username, site, admin_pw)
        if stored_password:
            # Mostramos el resultado en el label
            result_text = f"Contraseña recuperada para {username} en {site}"
            self.result_label.config(text=result_text)
            
            # Mostramos también en un diálogo de mensaje
            messagebox.showinfo("Contraseña Recuperada", 
                              f"Contraseña para {username} en {site}:\n\n{stored_password}\n\n"
                              "La contraseña se ha copiado al portapapeles.")
            
            # Copiar al portapapeles
            self.root.clipboard_clear()
            self.root.clipboard_append(stored_password)
            
            # Limpiar campos
            self.rec_user_entry.delete(0, tk.END)
            self.rec_site_entry.delete(0, tk.END)
            self.admin_pass_entry.delete(0, tk.END)
        else:
            self.result_label.config(text="Error: No se encontró la credencial")

    def list_passwords(self):
        """Lista todas las credenciales almacenadas"""
        admin_pw = self.list_admin_entry.get()
        
        if not self.verify_admin_password_gui(admin_pw):
            return

        # Limpiar el árbol
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener credenciales
        credentials = list_credentials(admin_pw)
        
        # Limpiar campo de contraseña de admin después de usarla
        self.list_admin_entry.delete(0, tk.END)
        
        if credentials:
            for username, site in credentials:
                self.tree.insert("", tk.END, values=(username, site))
            messagebox.showinfo("Éxito", f"Mostrando {len(credentials)} credenciales")
        else:
            messagebox.showinfo("Info", "No hay credenciales almacenadas")
            
    def remove_password(self):
        """Elimina una credencial almacenada"""
        username = self.del_user_entry.get()
        site = self.del_site_entry.get()
        admin_pw = self.del_admin_entry.get()

        if not all([username, site, admin_pw]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        if not self.verify_admin_password_gui(admin_pw):
            return

        if delete_password(username, site, admin_pw):
            messagebox.showinfo("Éxito", "Credencial eliminada correctamente")
            self.del_user_entry.delete(0, tk.END)
            self.del_site_entry.delete(0, tk.END)
            self.del_admin_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "No se pudo eliminar la credencial")

    def clear_entries(self):
        """Limpia los campos de entrada"""
        self.user_entry.delete(0, tk.END)
        self.site_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)

def main():
    ensure_passwd_dir()
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()