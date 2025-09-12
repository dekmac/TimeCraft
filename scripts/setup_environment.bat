@echo off
echo 🚀 TimeCraft Environment Setup (Windows)
echo ================================================

REM Check if conda is installed
conda --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Conda is not installed or not in PATH
    echo Please install Miniconda or Anaconda first
    pause
    exit /b 1
)

echo ✅ Conda is installed

REM Check if environment exists
conda env list | findstr "timecraft" >nul
if %errorlevel% equ 0 (
    echo ✅ Conda environment 'timecraft' already exists
    echo 📦 Updating conda environment...
    conda env update -f environment.yml --prune
    if %errorlevel% neq 0 (
        echo ⚠️  Warning: Failed to update conda environment
    )
) else (
    echo 📦 Creating new conda environment...
    conda env create -f environment.yml
    if %errorlevel% neq 0 (
        echo ❌ Failed to create conda environment
        pause
        exit /b 1
    )
    echo ✅ Conda environment created successfully
)

REM Install TimeCraft.Api requirements
if exist "TimeCraft.Api\BRIDGE\requirements.txt" (
    echo 📦 Installing BRIDGE requirements...
    conda run -n timecraft pip install -r TimeCraft.Api\BRIDGE\requirements.txt
    if %errorlevel% neq 0 (
        echo ⚠️  Warning: Failed to install BRIDGE requirements
    ) else (
        echo ✅ BRIDGE requirements installed
    )
)

REM Install additional packages
echo 📦 Installing additional packages...
conda run -n timecraft pip install fastapi uvicorn python-multipart jinja2 aiofiles
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Failed to install additional packages
) else (
    echo ✅ Additional packages installed
)

echo.
echo 🎉 Environment setup complete!
echo.
echo To activate the environment, run:
echo   conda activate timecraft
echo.
echo To start the API server, run:
echo   python TimeCraft.Api\TimeCraft.Api\main.py
echo.
pause
