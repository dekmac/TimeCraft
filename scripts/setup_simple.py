#!/usr/bin/env python3
"""
Simple TimeCraft Setup for Python Virtual Environment
Fallback when conda is not available
"""

import subprocess
import sys
import venv
from pathlib import Path


def create_venv_and_install():
    """Create virtual environment and install basic requirements"""
    venv_path = "venv"
    
    print("🚀 TimeCraft Simple Setup (Python venv)")
    print("=" * 50)
    
    # Create virtual environment
    if not Path(venv_path).exists():
        print(f"📦 Creating virtual environment in '{venv_path}'...")
        try:
            venv.create(venv_path, with_pip=True)
            print("✅ Virtual environment created")
        except Exception as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Get pip path
    if sys.platform == "win32":
        pip_exe = Path(venv_path) / "Scripts" / "pip.exe"
        python_exe = Path(venv_path) / "Scripts" / "python.exe"
    else:
        pip_exe = Path(venv_path) / "bin" / "pip"
        python_exe = Path(venv_path) / "bin" / "python"
    
    # Install basic requirements
    basic_packages = [
        "fastapi",
        "uvicorn",
        "jinja2",
        "aiofiles",
        "numpy",
        "pandas", 
        "matplotlib",
        "scikit-learn",
        "python-multipart",
        "requests"
    ]
    
    print("📦 Installing basic packages...")
    for package in basic_packages:
        print(f"  Installing {package}...")
        try:
            subprocess.run([str(pip_exe), "install", package], check=True, capture_output=True)
            print(f"  ✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Warning: Failed to install {package}")
    
    print("\n🎉 Simple setup complete!")
    print("\nTo activate the environment:")
    if sys.platform == "win32":
        print(f"  {venv_path}\\Scripts\\activate")
    else:
        print(f"  source {venv_path}/bin/activate")
    
    print("\nTo start the API server:")
    print(f"  {python_exe} TimeCraft.Api/TimeCraft.Api/main.py")
    
    return True


if __name__ == "__main__":
    success = create_venv_and_install()
    sys.exit(0 if success else 1)
