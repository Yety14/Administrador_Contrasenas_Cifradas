import os
import subprocess
import sys
from password_manager import ensure_passwd_dir, init_database, get_cipher_key

def create_executable():
    """Create standalone executable for the Password Manager"""
    try:
        # Get absolute path of current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Paths to include
        main_script = os.path.join(current_dir, 'main.py')
        password_manager_script = os.path.join(current_dir, 'password_manager.py')
        requirements_file = os.path.join(current_dir, 'requirements.txt')
        passwd_dir = os.path.join(current_dir, 'passwd')

        # Verify required files exist
        if not os.path.exists(main_script):
            raise FileNotFoundError(f"main.py not found in {current_dir}")
        if not os.path.exists(password_manager_script):
            raise FileNotFoundError(f"password_manager.py not found in {current_dir}")
        if not os.path.exists(requirements_file):
            raise FileNotFoundError(f"requirements.txt not found in {current_dir}")
        if not os.path.exists(passwd_dir):
            raise FileNotFoundError(f"passwd directory not found in {current_dir}")

        # Run PyInstaller command
        subprocess.check_call([
            sys.executable, '-m', 'PyInstaller',
            '--onefile',           # Create a single executable
            '--windowed',          # No console window
            '--name=PasswordManager',  # Name of the executable
            '--clean',             # Remove previous build cache
            f'--add-data={password_manager_script};.',  # Include password_manager.py
            f'--add-data={passwd_dir};passwd',          # Include passwd directory (DB and key)
            main_script            # Main script to package
        ])
        print("✓ Executable created successfully in 'dist' directory!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating executable: {e}")
    except Exception as e:
        import traceback
        print(f"✗ Unexpected error: {e}")
        traceback.print_exc()

def check_dependencies():
    """Check and install required dependencies from requirements.txt"""
    try:
        # Path to requirements.txt
        script_dir = os.path.dirname(os.path.abspath(__file__))
        requirements_file = os.path.join(script_dir, 'requirements.txt')

        # Install dependencies using pip
        print("Installing dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print("All dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def initialize_environment():
    """Initialize the environment by creating necessary files and database"""
    print("Initializing environment...")
    ensure_passwd_dir()  # Create the directory for storing files
    admin_password = "admin123"  # Default admin password (you can prompt the user for this)
    init_database(admin_password)  # Initialize the database and admin credentials
    get_cipher_key()  # Generate or retrieve the encryption key
    print("Environment initialized successfully!")

def main():
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Check and install dependencies
    check_dependencies()

    # Initialize environment (create DB, key, etc.)
    initialize_environment()

    # Create executable
    create_executable()

if __name__ == '__main__':
    main()
