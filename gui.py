import os
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sqlite3
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
    PASSWD_DB
)

class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Contraseñas Seguro")
        self.root.geometry("800x600")
        self.setup_ui()
        self.bind_enter_key()
        
        if not os.path.exists(PASSWD_DB):
            self.setup_admin_password()

    def bind_enter_key(self):
        """Vincula la tecla Enter a los campos de entrada"""
        self.pass_entry.bind('<Return>', lambda event: self.save_password())
        self.admin_pass_entry.bind('<Return>', lambda event: self.recover_password())
        self.list_admin_entry.bind('<Return>', lambda event: self.list_passwords())
        self.del_admin_entry.bind('<Return>', lambda event: self.remove_password())

    def setup_ui(self):
        """Configura los elementos de la interfaz"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

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
            messagebox.showinfo("Éxito", "Contraseña de administrador configurada")
        else:
            messagebox.showerror("Error", "Debe establecer una contraseña de administrador")
            self.root.destroy()

    def create_save_tab(self):
        """Pestaña para guardar/actualizar contraseñas"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Guardar/Actualizar")

        ttk.Label(tab, text="Usuario:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.user_entry = ttk.Entry(tab)
        self.user_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(tab, text="Sitio/Aplicación:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.site_entry = ttk.Entry(tab)
        self.site_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(tab, text="Contraseña:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.pass_entry = ttk.Entry(tab, show="*")
        self.pass_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ttk.Button(tab, text="Guardar", command=self.save_password).grid(
            row=3, column=0, columnspan=2, pady=10)

        tab.columnconfigure(1, weight=1)

    def create_recover_tab(self):
        """Pestaña para recuperar contraseñas"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Recuperar")

        ttk.Label(tab, text="Usuario:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.rec_user_entry = ttk.Entry(tab)
        self.rec_user_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(tab, text="Sitio/Aplicación:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.rec_site_entry = ttk.Entry(tab)
        self.rec_site_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(tab, text="Contraseña Admin:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.admin_pass_entry = ttk.Entry(tab, show="*")
        self.admin_pass_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.result_var = tk.StringVar()
        ttk.Label(tab, textvariable=self.result_var, wraplength=300).grid(
            row=4, column=0, columnspan=2, pady=10)

        ttk.Button(tab, text="Recuperar", command=self.recover_password).grid(
            row=3, column=0, columnspan=2, pady=10)

        tab.columnconfigure(1, weight=1)

    def create_list_tab(self):
        """Pestaña para listar credenciales"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Listar")

        ttk.Label(tab, text="Contraseña Admin:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.list_admin_entry = ttk.Entry(tab, show="*")
        self.list_admin_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.tree = ttk.Treeview(tab, columns=("Usuario", "Sitio"), show="headings")
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Sitio", text="Sitio/Aplicación")
        self.tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        ttk.Button(tab, text="Mostrar Credenciales", command=self.list_passwords).grid(
            row=2, column=0, columnspan=2, pady=10)

        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)

    def create_delete_tab(self):
        """Pestaña para eliminar credenciales"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Eliminar")

        ttk.Label(tab, text="Usuario:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.del_user_entry = ttk.Entry(tab)
        self.del_user_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(tab, text="Sitio/Aplicación:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.del_site_entry = ttk.Entry(tab)
        self.del_site_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(tab, text="Contraseña Admin:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.del_admin_entry = ttk.Entry(tab, show="*")
        self.del_admin_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ttk.Button(tab, text="Eliminar", command=self.remove_password).grid(
            row=3, column=0, columnspan=2, pady=10)

        tab.columnconfigure(1, weight=1)

    def save_password(self, event=None):
        username = self.user_entry.get()
        site = self.site_entry.get()
        password = self.pass_entry.get()

        if not all([username, site, password]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        # Verificar si ya existe la credencial
        if check_duplicate(username, site):
            # Mostrar diálogo de confirmación personalizado
            confirm = tk.Toplevel(self.root)
            confirm.title("Confirmar Sobreescritura")
            confirm.geometry("400x150")
            confirm.resizable(False, False)
            
            # Centrar la ventana de confirmación
            window_width = confirm.winfo_reqwidth()
            window_height = confirm.winfo_reqheight()
            position_right = int(confirm.winfo_screenwidth()/2 - window_width/2)
            position_down = int(confirm.winfo_screenheight()/2 - window_height/2)
            confirm.geometry(f"+{position_right}+{position_down}")
            
            tk.Label(confirm, text=f"Ya existe una contraseña para {username} en {site}").pack(pady=10)
            tk.Label(confirm, text="¿Desea sobreescribirla?").pack()
            
            def on_yes():
                admin_pw = simpledialog.askstring("Admin", "Ingrese contraseña de administrador:", 
                                                parent=confirm, show='*')
                if admin_pw and verify_admin_password(admin_pw):
                    if update_password(username, site, password):
                        messagebox.showinfo("Éxito", "Contraseña actualizada correctamente", parent=confirm)
                        self.user_entry.delete(0, tk.END)
                        self.site_entry.delete(0, tk.END)
                        self.pass_entry.delete(0, tk.END)
                    else:
                        messagebox.showerror("Error", "No se pudo actualizar la contraseña", parent=confirm)
                else:
                    messagebox.showerror("Error", "Contraseña de administrador incorrecta", parent=confirm)
                confirm.destroy()
            
            def on_no():
                confirm.destroy()
            
            btn_frame = tk.Frame(confirm)
            btn_frame.pack(pady=10)
            
            tk.Button(btn_frame, text="Sí", command=on_yes, width=10).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="No", command=on_no, width=10).pack(side=tk.RIGHT, padx=10)
            
            confirm.grab_set()
            self.root.wait_window(confirm)
        else:
            # Si no existe, guardar normalmente
            if store_password(username, site, password):
                messagebox.showinfo("Éxito", "Contraseña guardada correctamente")
                self.user_entry.delete(0, tk.END)
                self.site_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)
                
    def recover_password(self, event=None):
        username = self.rec_user_entry.get()
        site = self.rec_site_entry.get()
        admin_pw = self.admin_pass_entry.get()

        if not all([username, site, admin_pw]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        password = recover_password(username, site, admin_pw)
        if password:
            self.result_var.set(f"Contraseña recuperada: {password}")
        else:
            self.result_var.set("No se pudo recuperar la contraseña")

    def list_passwords(self, event=None):
        admin_pw = self.list_admin_entry.get()
        
        if not verify_admin_password(admin_pw):
            messagebox.showerror("Error", "Contraseña de administrador incorrecta")
            return

        # Limpiar el árbol
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener credenciales
        conn = sqlite3.connect(PASSWD_DB)
        c = conn.cursor()
        c.execute("SELECT username, site FROM credentials ORDER BY username, site")
        credentials = c.fetchall()
        conn.close()
        
        if credentials:
            for username, site in credentials:
                self.tree.insert("", tk.END, values=(username, site))
            messagebox.showinfo("Éxito", f"Mostrando {len(credentials)} credenciales")
        else:
            messagebox.showinfo("Info", "No hay credenciales almacenadas")

    def remove_password(self, event=None):
        username = self.del_user_entry.get()
        site = self.del_site_entry.get()
        admin_pw = self.del_admin_entry.get()

        if not all([username, site, admin_pw]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        if delete_password(username, site, admin_pw):
            messagebox.showinfo("Éxito", "Credencial eliminada correctamente")
            self.del_user_entry.delete(0, tk.END)
            self.del_site_entry.delete(0, tk.END)
            self.del_admin_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "No se pudo eliminar la credencial")

def main():
    ensure_passwd_dir()
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    
'''
La implementación de estas mejoras de seguridad es totalmente viable y te detallo cada una con su nivel de complejidad:

### 1. **Borrado seguro de contraseñas temporales** (Complejidad: Media-Baja)
- **Implementación**: Usar arrays de bytes mutables en lugar de strings (que son inmutables y permanecen en memoria)
- **Beneficio**: Las contraseñas no quedan residentes en memoria
- **Desafío**: Requiere cambios en el manejo de strings en el código
- **Herramientas**: `bytearray` en Python + overwrite explícito

### 2. **Sistema de permisos mínimos en BD** (Complejidad: Media)
- **Implementación**:
  - Crear usuario de BD con permisos solo CRUD necesarios
  - Revocar permisos a tablas del sistema
- **Beneficio**: Limita daño en caso de inyección SQL
- **Desafío**: Requiere configuración manual inicial
- **SQL Ejemplo**: 
```sql
CREATE USER 'passmanager'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE, DELETE ON database.credentials TO 'passmanager'@'localhost';
```

### 3. **Ocultar contraseñas en memoria** (Complejidad: Media-Alta)
- **Implementación**:
  - Usar librerías especializadas como `keyring`
  - Almacenar en estructuras no paginables
- **Beneficio**: Previene lectura desde swap/volcados memoria
- **Desafío**: Requiere dependencias externas en Python

### 4. **Guardar admin key en archivo separado** (Complejidad: Baja)
- **Implementación**:
  - Dividir la clave en 2 partes (archivo + variable entorno)
  - Usar `configparser` para manejo seguro
- **Beneficio**: Defense in depth
- **Ejemplo Estructura**:
```
/passwd/
  ├── passwords.db
  ├── secret.key (clave cifrado)
  └── admin.key (hash admin separado)
```

### 5. **Bloqueo después de 5 intentos** (Complejidad: Media)
- **Implementación**:
  - Tabla de intentos fallidos con timestamp
  - Temporizador progresivo (ej. 2^n segundos)
- **Beneficio**: Previene fuerza bruta
- **SQL sugerido**:
```sql
CREATE TABLE login_attempts (
  ip VARCHAR(45),
  attempts INT,
  last_attempt DATETIME,
  locked_until DATETIME
);
```

### Viabilidad General:
| Mejora            | Tiempo Estimado | Riesgo Implementación | Impacto Seguridad |
|-------------------|-----------------|-----------------------|-------------------|
| Borrado seguro    | 2-3 horas       | Bajo                  | Alto              |
| Permisos BD       | 1-2 horas       | Medio                 | Medio-Alto        |
| Ocultar memoria   | 4-5 horas       | Alto                  | Medio             |
| Admin key separada| 1 hora          | Bajo                  | Medio             |
| Bloqueo intentos  | 3-4 horas       | Medio                 | Alto              |

### Recomendación de Implementación:
1. **Primera Fase** (Seguridad básica reforzada):
   - Admin key separada + Bloqueo por intentos
   - Estas son las de mayor impacto/relación esfuerzo-beneficio

2. **Segunda Fase** (Protección avanzada):
   - Borrado seguro + Permisos BD
   - Requieren más cambios pero mejoran significativamente

3. **Tercera Fase** (Protección memoria):
   - Ocultar contraseñas en memoria
   - Más compleja pero útil si manejas datos muy sensibles

¿Quieres que desarrolle más detalles de implementación para alguna en particular? Podría proporcionarte ejemplos de código específicos para las que elijas primero.
'''