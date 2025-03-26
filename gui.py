import os
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
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
        self.configure_styles()
        self.setup_ui()
        
        if not os.path.exists(PASSWD_DB):
            self.setup_admin_password()

    def configure_styles(self):
        """Configura estilos modernos para la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme

        # Color palette
        bg_color = '#f0f0f0'
        primary_color = '#3498db'
        secondary_color = '#2ecc71'
        text_color = '#2c3e50'
        
        # Configure root
        self.root.configure(bg=bg_color)

        # Notebook style
        style.configure('TNotebook', background=bg_color)
        style.map('TNotebook.Tab', 
            background=[('selected', primary_color), ('!selected', '#bdc3c7')],
            foreground=[('selected', 'white'), ('!selected', text_color)]
        )

        # Button styles
        style.configure('TButton', 
            font=('Arial', 10, 'bold'),
            background=primary_color,
            foreground='white',
            padding=10
        )
        style.map('TButton',
            background=[('active', secondary_color)]
        )

        # Entry styles
        style.configure('TEntry', 
            font=('Arial', 10),
            padding=5
        )

        # Label styles
        style.configure('TLabel', 
            font=('Arial', 10, 'bold'),
            background=bg_color,
            foreground=text_color
        )

        # Treeview styles
        style.configure('Treeview', 
            background='white',
            foreground=text_color,
            rowheight=25,
            font=('Arial', 10)
        )
        style.configure('Treeview.Heading', 
            font=('Arial', 10, 'bold'),
            background=primary_color,
            foreground='white'
        )

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
                  font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,20))

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
            tab.columnconfigure(1, weight=1)

        # Botón de guardar con estilo
        save_btn = ttk.Button(tab, text="💾 Guardar", command=self.save_password)
        save_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        self.pass_entry.bind("<Return>", lambda event: self.save_password())

    def create_recover_tab(self):
        """Pestaña para recuperar contraseñas con diseño mejorado"""
        tab = ttk.Frame(self.notebook, padding="20 20 20 20")
        self.notebook.add(tab, text=" 🔍 Recuperar ")

        # Título de sección
        ttk.Label(tab, text="Recuperar Contraseña", 
                  font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,20))

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
            tab.columnconfigure(1, weight=1)

        self.result_var = tk.StringVar()
        ttk.Label(tab, textvariable=self.result_var, wraplength=300).grid(
            row=len(fields)+1, column=0, columnspan=2, pady=10)

        recover_btn = ttk.Button(tab, text="🔍 Recuperar", command=self.recover_password)
        recover_btn.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
        
        self.admin_pass_entry.bind("<Return>", lambda event: self.recover_password())

    def create_list_tab(self):
        """Pestaña para listar credenciales con diseño mejorado"""
        tab = ttk.Frame(self.notebook, padding="20 20 20 20")
        self.notebook.add(tab, text=" 📋 Listar ")

        # Título de sección
        ttk.Label(tab, text="Listar Credenciales", 
                  font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,20))

        ttk.Label(tab, text="🔒 Contraseña Admin:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.list_admin_entry = ttk.Entry(tab, show="*", width=40)
        self.list_admin_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Treeview con estilo mejorado
        self.tree = ttk.Treeview(tab, columns=("Usuario", "Sitio"), show="headings", height=10)
        self.tree.heading("Usuario", text="👤 Usuario")
        self.tree.heading("Sitio", text="🌐 Sitio/Aplicación")
        self.tree.column("Usuario", width=200)
        self.tree.column("Sitio", width=300)
        self.tree.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=2, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        list_btn = ttk.Button(tab, text="📋 Mostrar Credenciales", command=self.list_passwords)
        list_btn.grid(row=3, column=0, columnspan=2, pady=20)

        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(2, weight=1)
        self.list_admin_entry.bind("<Return>", lambda event: self.list_passwords())

    def create_delete_tab(self):
        """Pestaña para eliminar credenciales con diseño mejorado"""
        tab = ttk.Frame(self.notebook, padding="20 20 20 20")
        self.notebook.add(tab, text=" ❌ Eliminar ")

        # Título de sección
        ttk.Label(tab, text="Eliminar Credencial", 
                  font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,20))

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
            tab.columnconfigure(1, weight=1)

        delete_btn = ttk.Button(tab, text="❌ Eliminar", command=self.remove_password)
        delete_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        self.del_admin_entry.bind("<Return>", lambda event: self.remove_password())

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
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        if not self.verify_admin_password_gui(admin_pw):
            return

        stored_password = recover_password(username, site, admin_pw)
        if stored_password:
            # Mostrar la contraseña recuperada en un diálogo seguro
            messagebox.showinfo("Contraseña Recuperada", 
                            f"Contraseña para --{username}-- en --{site}-- recuperada exitosamente.\n\n"
                            f"Contraseña:   {stored_password}\n\n\n"
                            "La contraseña se ha copiado al portapapeles para su uso.")
        
            # Copiar al portapapeles para mayor seguridad
            self.root.clipboard_clear()
            self.root.clipboard_append(stored_password)
            
            # Limpiar los campos de entrada
            self.rec_user_entry.delete(0, tk.END)
            self.rec_site_entry.delete(0, tk.END)
            self.admin_pass_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "No se encontró la credencial o la contraseña de administrador es incorrecta")

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