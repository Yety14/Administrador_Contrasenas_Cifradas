import os
import hashlib
import sqlite3
from cryptography.fernet import Fernet
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWD_DIR = os.path.join(BASE_DIR, "passwd")
PASSWD_DB = os.path.join(PASSWD_DIR, "passwords.db")
SECRET_KEY_FILE = os.path.join(PASSWD_DIR, "secret.key")

def ensure_passwd_dir():
    os.makedirs(PASSWD_DIR, exist_ok=True)
    if os.name == 'posix':
        os.chmod(PASSWD_DIR, 0o700)

def get_cipher_key():
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

KEY = get_cipher_key()
cipher_suite = Fernet(KEY)

def encrypt_password(password):
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

def init_database(admin_password):
    ensure_passwd_dir()
    if not os.path.exists(PASSWD_DB):
        conn = sqlite3.connect(PASSWD_DB)
        c = conn.cursor()
        
        # Crear tabla para credenciales
        c.execute('''CREATE TABLE credentials
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL,
                      site TEXT NOT NULL,
                      encrypted_password TEXT NOT NULL,
                      UNIQUE(username, site))''')
        
        # Crear tabla para admin
        hashed_admin_pw = hashlib.sha256(admin_password.encode()).hexdigest()
        c.execute('''CREATE TABLE admin
                     (id INTEGER PRIMARY KEY,
                      password_hash TEXT NOT NULL)''')
        c.execute("INSERT INTO admin VALUES (1, ?)", (hashed_admin_pw,))
        
        conn.commit()
        conn.close()
        os.chmod(PASSWD_DB, 0o600)

def verify_admin_password(attempt):
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM admin WHERE id = 1")
    result = c.fetchone()
    conn.close()
    
    if result:
        stored_hash = result[0]
        return hashlib.sha256(attempt.encode()).hexdigest() == stored_hash
    return False

def check_duplicate(username, site):
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT 1 FROM credentials WHERE username = ? AND site = ?", (username, site))
    result = c.fetchone()
    conn.close()
    return result is not None

def store_password(username, site, password):
    encrypted_pw = encrypt_password(password)
    
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO credentials (username, site, encrypted_password) VALUES (?, ?, ?)",
                 (username, site, encrypted_pw))
        conn.commit()
        print("✓ Contraseña guardada!")
        return True
    except sqlite3.IntegrityError:
        print("✓ Ya existe una entrada para este usuario y sitio")
        admin_pw = input("¿Desea cambiar la contraseña? (s/n): ")
        if admin_pw.lower() == 's':
            admin_pw = input("Contraseña de administrador: ")
            if verify_admin_password(admin_pw):
                update_password(username, site, password)
                return True
        return False
    finally:
        conn.close()

def update_password(username, site, new_password):
    encrypted_pw = encrypt_password(new_password)
    
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("UPDATE credentials SET encrypted_password = ? WHERE username = ? AND site = ?",
             (encrypted_pw, username, site))
    rows_updated = c.rowcount
    conn.commit()
    conn.close()
    
    if rows_updated > 0:
        print("✓ Contraseña actualizada exitosamente")
        return True
    else:
        print("✗ No se encontró la entrada para actualizar")
        return False

def recover_password(username, site, admin_password):
    if not verify_admin_password(admin_password):
        print("✗ Contraseña de administrador incorrecta")
        return None
    
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT encrypted_password FROM credentials WHERE username = ? AND site = ?",
             (username, site))
    result = c.fetchone()
    conn.close()
    
    if result:
        return decrypt_password(result[0])
    return None

def list_credentials(admin_password):
    if not verify_admin_password(admin_password):
        print("✗ Contraseña de administrador incorrecta")
        return
    
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT username, site FROM credentials ORDER BY username, site")
    credentials = c.fetchall()
    conn.close()
    
    print("\n=== LISTADO DE CREDENCIALES REGISTRADAS ===")
    print("{:<20} {:<30}".format("USUARIO", "SITIO"))
    print("-" * 50)
    
    for username, site in credentials:
        print("{:<20} {:<30}".format(username, site))
    
    print("\nTotal registros:", len(credentials))

def delete_password(username, site, admin_password):
    if not verify_admin_password(admin_password):
        print("✗ Contraseña de administrador incorrecta")
        return False
    
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("DELETE FROM credentials WHERE username = ? AND site = ?", (username, site))
    rows_deleted = c.rowcount
    conn.commit()
    conn.close()
    
    if rows_deleted > 0:
        print(f"✓ Entrada para '{username}' en '{site}' eliminada")
        return True
    else:
        print("✗ No se encontró la entrada especificada")
        return False

def count_entries():
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM credentials")
    count = c.fetchone()[0]
    conn.close()
    return count

def main():
    ensure_passwd_dir()
    if not os.path.exists(PASSWD_DB):
        admin_pw = input("Establezca la contraseña de administrador: ")
        init_database(admin_pw)
    
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Guardar/Actualizar contraseña")
        print("2. Recuperar contraseña")
        print("3. Listar credenciales")
        print("4. Eliminar contraseña")
        print("5. Salir")
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            username = input("Usuario: ")
            site = input("Sitio: ")
            password = input("Contraseña: ")
            store_password(username, site, password)
            input("\nPresione Enter para continuar...")
            
        elif opcion == "2":
            username = input("Usuario a recuperar: ")
            site = input("Sitio a recuperar: ")
            admin_pw = input("Contraseña de administrador: ")
            
            recovered = recover_password(username, site, admin_pw)
            if recovered:
                print(f"✓ Contraseña recuperada: {recovered}")
            else:
                print("✗ No se pudo recuperar la contraseña")
            input("\nPresione Enter para continuar...")
                
        elif opcion == "3":
            admin_pw = input("Contraseña de administrador: ")
            list_credentials(admin_pw)
            input("\nPresione Enter para continuar...")
                
        elif opcion == "4":
            username = input("Usuario a eliminar: ")
            site = input("Sitio a eliminar: ")
            admin_pw = input("Contraseña de administrador: ")
            delete_password(username, site, admin_pw)
            input("\nPresione Enter para continuar...")
            
        elif opcion == "5":
            print("Saliendo del sistema...")
            break
            
        else:
            print("✗ Opción no válida")
            input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()