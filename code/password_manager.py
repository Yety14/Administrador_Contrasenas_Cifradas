import os
import hashlib
import sqlite3
import hmac
import base64
import random
import string
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

def ensure_passwd_dir():
    """Crea el directorio seguro con permisos adecuados"""
    os.makedirs(PASSWD_DIR, exist_ok=True)
    if os.name == 'posix':
        os.chmod(PASSWD_DIR, 0o700)

def init_database(admin_password):
    """Inicializa la base de datos y archivos de seguridad"""
    ensure_passwd_dir()

    if not os.path.exists(PASSWD_DB):
        with sqlite3.connect(PASSWD_DB) as conn:
            c = conn.cursor()
            # Crear tablas
            c.execute('''CREATE TABLE IF NOT EXISTS credentials
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT NOT NULL,
                          site TEXT NOT NULL,
                          encrypted_password TEXT NOT NULL,
                          UNIQUE(username, site))''')

            c.execute('''CREATE TABLE IF NOT EXISTS login_attempts
                         (id INTEGER PRIMARY KEY,
                          attempts INTEGER DEFAULT 0,
                          last_attempt TIMESTAMP,
                          locked_until TIMESTAMP)''')
            c.execute("INSERT INTO login_attempts VALUES (1, 0, NULL, NULL)")

        os.chmod(PASSWD_DB, 0o600)
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
    hashed_pw = hashlib.pbkdf2_hmac('sha512', password.encode(), salt, PBKDF2_ITERATIONS)
    with open(ADMIN_CREDENTIALS_FILE, 'wb') as f:
        f.write(salt + hashed_pw)
    os.chmod(ADMIN_CREDENTIALS_FILE, 0o600)

def verify_admin_password(attempt):
    """Verifica la contraseña admin con protección contra fuerza bruta"""
    with sqlite3.connect(PASSWD_DB) as conn:
        c = conn.cursor()
        c.execute("SELECT attempts, locked_until FROM login_attempts WHERE id = 1")
        attempts, locked_until = c.fetchone()

        if locked_until and datetime.now() < datetime.fromisoformat(locked_until):
            return False

        try:
            with open(ADMIN_CREDENTIALS_FILE, 'rb') as f:
                data = f.read()
                salt = data[:16]
                stored_hash = data[16:]
                attempt_hash = hashlib.pbkdf2_hmac('sha512', attempt.encode(), salt, PBKDF2_ITERATIONS)

                if hmac.compare_digest(stored_hash, attempt_hash):
                    c.execute("UPDATE login_attempts SET attempts = 0, locked_until = NULL WHERE id = 1")
                    conn.commit()
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
        return False

def store_password(username, site, password):
    """Almacena una nueva contraseña o actualiza una existente"""
    encrypted_pw = encrypt_password(password)
    with sqlite3.connect(PASSWD_DB) as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO credentials (username, site, encrypted_password) VALUES (?, ?, ?)",
                     (username, site, encrypted_pw))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            conn.rollback()
            return False

def recover_password(username, site, admin_password):
    """Verifica si la contraseña admin es correcta y recupera una contraseña almacenada"""
    if not verify_admin_password(admin_password):
        return None
    
    with sqlite3.connect(PASSWD_DB) as conn:
        c = conn.cursor()
        c.execute("SELECT encrypted_password FROM credentials WHERE username = ? AND site = ?", (username, site))
        result = c.fetchone()
    
    return decrypt_password(result[0]) if result else None

def list_credentials(admin_password):
    """Lista credenciales para la interfaz gráfica"""
    if not verify_admin_password(admin_password):
        return None
    
    with sqlite3.connect(PASSWD_DB) as conn:
        c = conn.cursor()
        c.execute("SELECT username, site FROM credentials ORDER BY username, site")
        return c.fetchall()

def delete_password(username, site, admin_password):
    """Elimina una credencial almacenada"""
    if not verify_admin_password(admin_password):
        return False
    
    with sqlite3.connect(PASSWD_DB) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM credentials WHERE username = ? AND site = ?", (username, site))
        rows_deleted = c.rowcount
        conn.commit()
    
    return rows_deleted > 0

def generate_password(length=16, use_upper=True, use_lower=True, use_numbers=True, use_special=True):
    """
    Genera una contraseña aleatoria segura con los parámetros especificados
    
    Args:
        length: Longitud de la contraseña (4-64)
        use_upper: Incluir mayúsculas
        use_lower: Incluir minúsculas
        use_numbers: Incluir números
        use_special: Incluir caracteres especiales
    
    Returns:
        str: Contraseña generada
    """
    if length < 4 or length > 64:
        raise ValueError("La longitud debe estar entre 4 y 64 caracteres")
    
    characters = []
    if use_upper:
        characters.extend(string.ascii_uppercase)
    if use_lower:
        characters.extend(string.ascii_lowercase)
    if use_numbers:
        characters.extend(string.digits)
    if use_special:
        characters.extend('!@#$%^&*()_+-=[]{}|;:,.<>?')
    
    if not characters:
        raise ValueError("Debe seleccionar al menos un tipo de caracteres")
    
    # Aseguramos que la contraseña tenga al menos un carácter de cada tipo seleccionado
    password = []
    if use_upper:
        password.append(random.choice(string.ascii_uppercase))
    if use_lower:
        password.append(random.choice(string.ascii_lowercase))
    if use_numbers:
        password.append(random.choice(string.digits))
    if use_special:
        password.append(random.choice('!@#$%^&*()_+-=[]{}|;:,.<>?'))
    
    # Completamos el resto de la contraseña con caracteres aleatorios
    remaining_length = length - len(password)
    password.extend(random.choice(characters) for _ in range(remaining_length))
    
    # Mezclamos los caracteres para mayor aleatoriedad
    random.shuffle(password)
    
    return ''.join(password)