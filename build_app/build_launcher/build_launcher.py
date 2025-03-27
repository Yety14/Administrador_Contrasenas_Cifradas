import os
import subprocess
import sys

def create_launcher_executable():
    """Create standalone launcher executable"""
    try:
        # Obtener la ruta absoluta del directorio actual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construir la ruta al archivo de especificaciones launch.spec
        spec_file = os.path.join(current_dir, 'launch.spec')
        
        # Verificar que el archivo launch.spec exista
        if not os.path.exists(spec_file):
            raise FileNotFoundError(f"launch.spec not found in {current_dir}")
        
        # Ejecutar el comando de PyInstaller con el archivo de especificaciones
        subprocess.check_call([
            sys.executable, '-m', 'PyInstaller', 
            '--clean',             # Eliminar la caché de compilaciones anteriores
            spec_file              # Archivo de especificaciones a utilizar
        ])
        
        print("Launcher executable created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error creating launcher executable: {e}")
    except Exception as e:
        import traceback
        print(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    create_launcher_executable()