#!/usr/bin/env python3
"""
TimeCraft Environment Setup Script
Ensures Python environment and dependencies are properly installed
Supports both conda and regular Python virtual environments
"""

import subprocess
import sys
import os
import json
import venv
from pathlib import Path


def run_command(cmd, shell=True, check=True, capture_output=False):
    """Run a command and return the result"""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=shell, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=shell, check=check)
            return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        return False


def check_conda_installed():
    """Check if conda is installed"""
    try:
        subprocess.run(["conda", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_python_venv():
    """Check if we can create Python virtual environments"""
    try:
        import venv
        return True
    except ImportError:
        return False


def check_venv_exists(venv_path="venv"):
    """Check if Python virtual environment exists"""
    venv_dir = Path(venv_path)
    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
    return python_exe.exists()


def create_python_venv(venv_path="venv"):
    """Create Python virtual environment"""
    print(f"Creating Python virtual environment in '{venv_path}'...")
    try:
        venv.create(venv_path, with_pip=True)
        return True
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        return False


def get_venv_python(venv_path="venv"):
    """Get path to Python executable in virtual environment"""
    venv_dir = Path(venv_path)
    if sys.platform == "win32":
        return str(venv_dir / "Scripts" / "python.exe")
    else:
        return str(venv_dir / "bin" / "python")


def get_venv_pip(venv_path="venv"):
    """Get path to pip executable in virtual environment"""
    venv_dir = Path(venv_path)
    if sys.platform == "win32":
        return str(venv_dir / "Scripts" / "pip.exe")
    else:
        return str(venv_dir / "bin" / "pip")


def install_requirements_venv(venv_path="venv"):
    """Install requirements in virtual environment"""
    pip_exe = get_venv_pip(venv_path)
    
    # Core requirements for TimeCraft
    core_packages = [
        "torch==1.13.0",
        "torchvision==0.14.0",
        "torchaudio==0.13.0",
        "numpy==1.19.2",
        "scikit-learn",
        "pandas",
        "matplotlib",
        "seaborn",
        "scipy",
        "tqdm",
        "jupyter",
        "statsmodels",
        "omegaconf",
        "einops",
        "fastapi",
        "uvicorn",
        "python-multipart",
        "jinja2",
        "aiofiles"
    ]
    
    print("Installing core packages...")
    for package in core_packages:
        print(f"Installing {package}...")
        if not run_command(f'"{pip_exe}" install {package}'):
            print(f"Warning: Failed to install {package}")
    
    # Install BRIDGE requirements
    bridge_req_path = Path("BRIDGE/requirements.txt")
    if bridge_req_path.exists():
        print("Installing BRIDGE requirements...")
        cmd = f'"{pip_exe}" install -r "{bridge_req_path}"'
        if not run_command(cmd):
            print("Warning: Failed to install BRIDGE requirements")
    
    return True


def check_environment_exists(env_name="timecraft"):
    """Check if conda environment exists"""
    try:
        result = subprocess.run(
            ["conda", "env", "list", "--json"],
            capture_output=True,
            check=True,
            text=True
        )
        envs = json.loads(result.stdout)
        env_paths = envs.get("envs", [])
        return any(env_name in path for path in env_paths)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return False


def create_conda_environment():
    """Create conda environment from environment.yml"""
    print("Creating conda environment 'timecraft'...")
    return run_command("conda env create -f environment.yml")


def update_conda_environment():
    """Update conda environment from environment.yml"""
    print("Updating conda environment 'timecraft'...")
    return run_command("conda env update -f environment.yml --prune")


def install_bridge_requirements():
    """Install BRIDGE-specific requirements"""
    print("Installing BRIDGE requirements...")
    bridge_req_path = Path("BRIDGE/requirements.txt")
    if bridge_req_path.exists():
        cmd = f"conda run -n timecraft pip install -r {bridge_req_path}"
        return run_command(cmd)
    return True


def install_additional_requirements():
    """Install any additional requirements"""
    additional_packages = [
        "fastapi",
        "uvicorn",
        "python-multipart",
        "jinja2",
        "aiofiles"
    ]
    
    print("Installing additional packages...")
    for package in additional_packages:
        if not run_command(f"conda run -n timecraft pip install {package}"):
            print(f"Warning: Failed to install {package}")


def main():
    """Main setup function"""
    print("🚀 TimeCraft Environment Setup")
    print("=" * 50)
    
    # Check if conda is installed
    conda_available = check_conda_installed()
    
    if conda_available:
        print("✅ Conda is installed")
        setup_with_conda()
    else:
        print("⚠️  Conda is not installed")
        print("🐍 Falling back to Python virtual environment")
        setup_with_venv()
    
    print("\n🎉 Environment setup complete!")
    print("\nTo run TimeCraft:")
    print("  Press F5 in VS Code and select 'TimeCraft Full Stack'")


def setup_with_conda():
    """Setup using conda environment"""
    # Check if environment exists
    env_exists = check_environment_exists()
    
    if not env_exists:
        print("📦 Creating new conda environment...")
        if not create_conda_environment():
            print("❌ Failed to create conda environment")
            sys.exit(1)
        print("✅ Conda environment created successfully")
    else:
        print("✅ Conda environment 'timecraft' already exists")
        print("📦 Updating conda environment...")
        if not update_conda_environment():
            print("⚠️  Warning: Failed to update conda environment")
    
    # Install BRIDGE requirements
    if not install_bridge_requirements():
        print("⚠️  Warning: Failed to install BRIDGE requirements")
    else:
        print("✅ BRIDGE requirements installed")
    
    # Install additional requirements
    install_additional_requirements()
    print("✅ Additional packages installed")
    
    print("\nTo activate the environment manually:")
    print("  conda activate timecraft")


def setup_with_venv():
    """Setup using Python virtual environment"""
    venv_path = "venv"
    
    # Check if we can create virtual environments
    if not check_python_venv():
        print("❌ Python venv module is not available")
        print("Please install Python with venv support")
        sys.exit(1)
    
    # Check if virtual environment exists
    if not check_venv_exists(venv_path):
        print(f"📦 Creating Python virtual environment in '{venv_path}'...")
        if not create_python_venv(venv_path):
            print("❌ Failed to create virtual environment")
            sys.exit(1)
        print("✅ Virtual environment created successfully")
    else:
        print("✅ Virtual environment already exists")
    
    # Install requirements
    print("📦 Installing Python packages...")
    if not install_requirements_venv(venv_path):
        print("⚠️  Warning: Some packages failed to install")
    else:
        print("✅ Python packages installed")
    
    venv_python = get_venv_python(venv_path)
    print(f"\nTo activate the environment manually:")
    if sys.platform == "win32":
        print(f"  {venv_path}\\Scripts\\activate.bat")
    else:
        print(f"  source {venv_path}/bin/activate")
    print(f"\nPython executable: {venv_python}")


if __name__ == "__main__":
    main()
