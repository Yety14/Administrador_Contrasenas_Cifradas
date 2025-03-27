import os
import subprocess
import sys

def main():
    # Obtener la ruta absoluta del directorio actual
    if getattr(sys, 'frozen', False):
        # La aplicación está congelada por PyInstaller
        current_dir = sys._MEIPASS
    else:
        # La aplicación no está congelada
        current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construir la ruta al script main.py
    main_script = os.path.join(current_dir, '../../code/main.py')
    
    # Verificar que el archivo main.py exista
    if not os.path.exists(main_script):
        raise FileNotFoundError(f"main.py not found in {current_dir}")
    
    # Ejecutar main.py
    subprocess.check_call([sys.executable, main_script])

if __name__ == '__main__':
    main()