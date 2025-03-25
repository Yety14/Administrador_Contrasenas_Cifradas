import os
import hashlib
import sqlite3
import hmac
import time
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

# Configuración de paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWD_DIR = os.path.join(BASE_DIR, "passwd")
PASSWD_DB = os.path.join(PASSWD_DIR, "passwords.db")
SECRET_KEY_FILE = os.path.join(PASSWD_DIR, "secret.key")
ADMIN_CREDENTIALS_FILE = os.path.join(PASSWD_DIR, "admin_credentials.secure")

# Configuración de seguridad
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutos en segundos
PBKDF2_ITERATIONS = 100000
SALT_SIZE = 16  # Tamaño del salt en bytes

def ensure_passwd_dir():
    """Crea el directorio seguro con permisos adecuados"""
    os.makedirs(PASSWD_DIR, exist_ok=True)
    if os.name == 'posix':
        os.chmod(PASSWD_DIR, 0o700)

def init_database(admin_password):
    """Inicializa la base de datos y archivos de seguridad"""
    ensure_passwd_dir()

    if not os.path.exists(PASSWD_DB):
        conn = sqlite3.connect(PASSWD_DB)
        c = conn.cursor()

        # Tabla de credenciales con cifrado
        c.execute('''CREATE TABLE credentials
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL,
                      site TEXT NOT NULL,
                      encrypted_password TEXT NOT NULL,
                      UNIQUE(username, site))''')

        # Tabla de intentos fallidos
        c.execute('''CREATE TABLE login_attempts
                     (id INTEGER PRIMARY KEY,
                      attempts INTEGER DEFAULT 0,
                      last_attempt TIMESTAMP,
                      locked_until TIMESTAMP)''')
        c.execute("INSERT INTO login_attempts VALUES (1, 0, NULL, NULL)")

        conn.commit()
        conn.close()
        os.chmod(PASSWD_DB, 0o600)

        # Guardar credenciales admin
        save_admin_credentials(admin_password)

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

def save_admin_credentials(password):
    """Guarda las credenciales admin de forma segura"""
    salt = os.urandom(16)
    hashed_pw = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode(),
        salt,
        PBKDF2_ITERATIONS
    )
    with open(ADMIN_CREDENTIALS_FILE, 'wb') as f:
        f.write(salt + hashed_pw)
    os.chmod(ADMIN_CREDENTIALS_FILE, 0o600)

def verify_admin_password(attempt):
    """Verifica la contraseña admin con protección contra fuerza bruta"""
    # Verificar estado de bloqueo
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT attempts, locked_until FROM login_attempts WHERE id = 1")
    attempts, locked_until = c.fetchone()

    if locked_until and datetime.now() < datetime.fromisoformat(locked_until):
        conn.close()
        return False

    # Verificar contraseña
    try:
        with open(ADMIN_CREDENTIALS_FILE, 'rb') as f:
            data = f.read()
            salt = data[:16]
            stored_hash = data[16:]
            attempt_hash = hashlib.pbkdf2_hmac(
                'sha512',
                attempt.encode(),
                salt,
                PBKDF2_ITERATIONS
            )

            if hmac.compare_digest(stored_hash, attempt_hash):
                # Resetear intentos si es correcta
                c.execute("UPDATE login_attempts SET attempts = 0, locked_until = NULL WHERE id = 1")
                conn.commit()
                conn.close()
                return True
    except FileNotFoundError:
        pass

    # Manejar intento fallido
    attempts += 1
    if attempts >= MAX_LOGIN_ATTEMPTS:
        locked_until = datetime.now() + timedelta(seconds=LOCKOUT_TIME)
        c.execute("UPDATE login_attempts SET attempts = ?, last_attempt = ?, locked_until = ? WHERE id = 1",
                 (attempts, datetime.now(), locked_until))
    else:
        c.execute("UPDATE login_attempts SET attempts = ?, last_attempt = ? WHERE id = 1",
                 (attempts, datetime.now()))

    conn.commit()
    conn.close()
    return False

def store_password(username, site, password):
    """Almacena una nueva contraseña o actualiza una existente"""
    encrypted_pw = encrypt_password(password)
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()

    try:
        # Intenta insertar primero
        c.execute("INSERT INTO credentials (username, site, encrypted_password) VALUES (?, ?, ?)",
                 (username, site, encrypted_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Si ya existe, pregunta si se desea actualizar
        conn.rollback()
        return False
    finally:
        conn.close()

def update_password(username, site, new_password):
    """Actualiza una contraseña existente con un nuevo hash y salt"""
    salt = generate_salt()
    hashed_pw = hash_password(new_password, salt)

    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("UPDATE credentials SET salt = ?, hashed_password = ? WHERE username = ? AND site = ?",
             (salt, hashed_pw, username, site))
    rows_updated = c.rowcount
    conn.commit()
    conn.close()

    return rows_updated > 0

def recover_password(username, site, admin_password):
    """Verifica si la contraseña admin es correcta y recupera una contraseña almacenada"""
    if not verify_admin_password(admin_password):
        return None

    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT salt, hashed_password FROM credentials WHERE username = ? AND site = ?", (username, site))
    result = c.fetchone()
    conn.close()

    return result  # Solo devuelve la información cifrada para validaciones

def check_duplicate(username, site):
    """Verifica si ya existe una entrada para el usuario y sitio dados"""
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT 1 FROM credentials WHERE username = ? AND site = ?", (username, site))
    exists = c.fetchone() is not None
    conn.close()
    return exists

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

def save_admin_credentials(password):
    """Guarda las credenciales admin de forma segura"""
    salt = os.urandom(16)
    hashed_pw = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode(),
        salt,
        PBKDF2_ITERATIONS
    )
    with open(ADMIN_CREDENTIALS_FILE, 'wb') as f:
        f.write(salt + hashed_pw)
    os.chmod(ADMIN_CREDENTIALS_FILE, 0o600)

def verify_admin_password(attempt):
    """Verifica la contraseña admin con protección contra fuerza bruta"""
    # Verificar estado de bloqueo
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT attempts, locked_until FROM login_attempts WHERE id = 1")
    attempts, locked_until = c.fetchone()

    if locked_until and datetime.now() < datetime.fromisoformat(locked_until):
        conn.close()
        return False

    # Verificar contraseña
    try:
        with open(ADMIN_CREDENTIALS_FILE, 'rb') as f:
            data = f.read()
            salt = data[:16]
            stored_hash = data[16:]
            attempt_hash = hashlib.pbkdf2_hmac(
                'sha512',
                attempt.encode(),
                salt,
                PBKDF2_ITERATIONS
            )

            if hmac.compare_digest(stored_hash, attempt_hash):
                # Resetear intentos si es correcta
                c.execute("UPDATE login_attempts SET attempts = 0, locked_until = NULL WHERE id = 1")
                conn.commit()
                conn.close()
                return True
    except FileNotFoundError:
        pass

    # Manejar intento fallido
    attempts += 1
    if attempts >= MAX_LOGIN_ATTEMPTS:
        locked_until = datetime.now() + timedelta(seconds=LOCKOUT_TIME)
        c.execute("UPDATE login_attempts SET attempts = ?, last_attempt = ?, locked_until = ? WHERE id = 1",
                 (attempts, datetime.now(), locked_until))
    else:
        c.execute("UPDATE login_attempts SET attempts = ?, last_attempt = ? WHERE id = 1",
                 (attempts, datetime.now()))

    conn.commit()
    conn.close()
    return False

def store_password(username, site, password):
    """Almacena una nueva contraseña o actualiza una existente"""
    encrypted_pw = encrypt_password(password)
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()

    try:
        # Intenta insertar primero
        c.execute("INSERT INTO credentials (username, site, encrypted_password) VALUES (?, ?, ?)",
                 (username, site, encrypted_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Si ya existe, pregunta si se desea actualizar
        conn.rollback()
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
    """
    Lista credenciales para la interfaz gráfica
    Devuelve una lista de tuplas con (usuario, sitio)
    """
    if not verify_admin_password(admin_password):
        return None
    
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT username, site FROM credentials ORDER BY username, site")
    credentials = c.fetchall()
    conn.close()
    
    return credentials

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