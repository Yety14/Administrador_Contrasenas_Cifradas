import os
import subprocess
import sys

def create_executable():
    """Create standalone executable for the Password Manager"""
    try:
        # Get absolute path of current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct paths
        gui_script = os.path.join(current_dir, 'gui.py')
        password_manager_script = os.path.join(current_dir, 'password_manager.py')

        # Verify files exist
        if not os.path.exists(gui_script):
            raise FileNotFoundError(f"gui.py not found in {current_dir}")
        if not os.path.exists(password_manager_script):
            raise FileNotFoundError(f"password_manager.py not found in {current_dir}")

        # Run PyInstaller command with --clean
        subprocess.check_call([
            sys.executable, '-m', 'PyInstaller', 
            '--onefile',           # Create a single executable
            '--windowed',          # No console window
            '--name=PasswordManager', # Name of the executable
            '--clean',             # Remove previous build cache
            gui_script              # Main script to package
        ])
        print("✓ Executable created successfully in 'dist' directory!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating executable: {e}")
    except Exception as e:
        import traceback
        print(f"✗ Unexpected error: {e}")
        traceback.print_exc()

def check_dependencies():
    """Check and install required dependencies"""
    dependencies = [
        'cryptography',
        'pyinstaller'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep} is already installed")
        except ImportError:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])

def main():
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Check and install dependencies
    check_dependencies()

    # Create executable
    create_executable()

if __name__ == '__main__':
    main()
