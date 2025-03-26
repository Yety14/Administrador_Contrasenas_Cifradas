import os
import sqlite3
import hashlib
import hmac
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

def init_database(admin_password):
    """Inicializa la base de datos"""
    ensure_passwd_dir()

    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()

    # Crear tabla de credenciales
    c.execute('''CREATE TABLE IF NOT EXISTS credentials (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  site TEXT NOT NULL,
                  encrypted_password TEXT NOT NULL,
                  UNIQUE(username, site))''')

    # Crear tabla de intentos fallidos
    c.execute('''CREATE TABLE IF NOT EXISTS login_attempts (
                  id INTEGER PRIMARY KEY,
                  attempts INTEGER DEFAULT 0,
                  last_attempt TIMESTAMP,
                  locked_until TIMESTAMP)''')
    
    c.execute("INSERT OR IGNORE INTO login_attempts VALUES (1, 0, NULL, NULL)")
    conn.commit()
    conn.close()

    # Guardar credenciales admin
    save_admin_credentials(admin_password)

def save_admin_credentials(password):
    """Guarda la contraseña admin de forma segura"""
    salt = os.urandom(16)
    hashed_pw = hashlib.pbkdf2_hmac('sha512', password.encode(), salt, PBKDF2_ITERATIONS)
    
    with open(ADMIN_CREDENTIALS_FILE, 'wb') as f:
        f.write(salt + hashed_pw)
    os.chmod(ADMIN_CREDENTIALS_FILE, 0o600)

def verify_admin_password(attempt):
    """Verifica la contraseña admin con protección contra ataques de fuerza bruta"""
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT attempts, locked_until FROM login_attempts WHERE id = 1")
    attempts, locked_until = c.fetchone()

    if locked_until and datetime.now() < datetime.fromisoformat(locked_until):
        conn.close()
        return False

    try:
        with open(ADMIN_CREDENTIALS_FILE, 'rb') as f:
            data = f.read()
            salt, stored_hash = data[:16], data[16:]
            attempt_hash = hashlib.pbkdf2_hmac('sha512', attempt.encode(), salt, PBKDF2_ITERATIONS)

            if hmac.compare_digest(stored_hash, attempt_hash):
                c.execute("UPDATE login_attempts SET attempts = 0, locked_until = NULL WHERE id = 1")
                conn.commit()
                conn.close()
                return True
    except FileNotFoundError:
        pass

    # Incrementar intentos fallidos
    attempts += 1
    if attempts >= MAX_LOGIN_ATTEMPTS:
        locked_until = datetime.now() + timedelta(seconds=LOCKOUT_TIME)
        c.execute("UPDATE login_attempts SET attempts = ?, locked_until = ? WHERE id = 1", (attempts, locked_until))
    else:
        c.execute("UPDATE login_attempts SET attempts = ? WHERE id = 1", (attempts,))
    
    conn.commit()
    conn.close()
    return False

def store_password(username, site, password):
    """Guarda una contraseña cifrada"""
    encrypted_pw = encrypt_password(password)
    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO credentials (username, site, encrypted_password) VALUES (?, ?, ?)", 
                  (username, site, encrypted_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()

def recover_password(username, site, admin_password):
    """Recupera una contraseña"""
    if not verify_admin_password(admin_password):
        return None

    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT encrypted_password FROM credentials WHERE username = ? AND site = ?", (username, site))
    result = c.fetchone()
    conn.close()

    return decrypt_password(result[0]) if result else None

def list_credentials(admin_password):
    """Lista todas las credenciales almacenadas"""
    if not verify_admin_password(admin_password):
        return None

    conn = sqlite3.connect(PASSWD_DB)
    c = conn.cursor()
    c.execute("SELECT username, site FROM credentials ORDER BY username, site")
    credentials = c.fetchall()
    conn.close()
    
    return credentials
