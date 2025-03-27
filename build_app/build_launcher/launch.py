import os
import subprocess
import sys

def main():
    # Obtener la ruta del directorio de instalación
    current_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = os.path.join(current_dir, "Python", "python.exe")
    
    # Verificar que el ejecutable de Python embebido existe
    if not os.path.exists(python_exe):
        raise FileNotFoundError(f"Python embebido no encontrado en {python_exe}")

    # Construir la ruta al script principal
    main_script = os.path.join(current_dir, "main.py")
    
    # Ejecutar el script con Python embebido
    subprocess.run([python_exe, main_script])

if __name__ == "__main__":
    main()
