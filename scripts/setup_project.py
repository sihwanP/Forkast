
import os
import subprocess
import sys

def run_command(command, cwd=None):
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        print("Output:", result.stdout)
        print("Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print("Output:", e.stdout)
        print("Errors:", e.stderr)
        raise

def main():
    base_dir = r"c:\dev\Forkast"
    if not os.path.exists(base_dir):
        print(f"Creating {base_dir}")
        os.makedirs(base_dir, exist_ok=True)
    
    os.chdir(base_dir)
    print(f"Current Dir: {os.getcwd()}")

    # 1. Create venv
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        run_command(f"{sys.executable} -m venv venv")
    
    # 2. Install Django
    print("Installing Django...")
    pip_exe = os.path.join(base_dir, "venv", "Scripts", "pip.exe")
    run_command(f'"{pip_exe}" install django')

    # 3. Start Project
    if not os.path.exists("forkast_project"):
        print("Creating Django project...")
        # We need to use the venv's python or django-admin
        django_admin = os.path.join(base_dir, "venv", "Scripts", "django-admin.exe")
        run_command(f'"{django_admin}" startproject forkast_project .')

    # 4. Start App
    if not os.path.exists("platform_ui"):
        print("Creating app platform_ui...")
        python_exe = os.path.join(base_dir, "venv", "Scripts", "python.exe")
        run_command(f'"{python_exe}" manage.py startapp platform_ui')

if __name__ == "__main__":
    main()
