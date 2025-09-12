# TimeCraft Scripts Directory

This directory contains environment setup and utility scripts for the TimeCraft project.

## 🚀 Environment Setup Scripts

### Quick Setup (Recommended)
- **`setup_simple.py`** - Creates Python virtual environment with basic dependencies
  - Use when conda is not available or for simple development setup
  - Creates `venv/` directory in project root
  - Installs FastAPI, uvicorn, and basic ML packages

### Full Setup (Production)
- **`setup_environment.ps1`** - PowerShell script for conda environment setup
  - Creates and manages conda environment named "timecraft"
  - Installs all ML dependencies from environment.yml
  - Installs BRIDGE requirements
  - **Usage**: `powershell -ExecutionPolicy Bypass -File scripts/setup_environment.ps1`

- **`setup_environment.bat`** - Batch file version of conda setup
  - Same functionality as PowerShell script
  - **Usage**: `scripts\setup_environment.bat`

## 🎯 VS Code Integration

These scripts are integrated with VS Code tasks:

- **`Ctrl+Shift+P` → "Tasks: Run Task"**
  - `setup-timecraft-environment` - Runs simple Python setup
  - `setup-conda-environment` - Runs full conda setup (PowerShell)
  - `setup-conda-environment-batch` - Runs full conda setup (Batch)

## 📁 Project Structure

```
TimeCraft/
├── scripts/                     # Top-level setup scripts
│   ├── setup_simple.py         # Simple Python venv setup
│   ├── setup_environment.ps1   # Conda setup (PowerShell)
│   └── setup_environment.bat   # Conda setup (Batch)
├── TimeCraft.Api/
│   └── scripts/                 # API-specific scripts
│       ├── setup_simple.py     # Copy for API directory
│       └── serve.py            # Development web server
└── TimeCraft.Web/              # .NET React application
```

## 🏃‍♂️ Quick Start

1. **For simple development**:
   ```bash
   python scripts/setup_simple.py
   venv/Scripts/activate              # Windows
   python TimeCraft.Api/TimeCraft.Api/main.py
   ```

2. **For full development (with conda)**:
   ```bash
   scripts/setup_environment.bat
   conda activate timecraft
   python TimeCraft.Api/TimeCraft.Api/main.py
   ```

3. **With VS Code**:
   - Press `F5` to start full-stack debugging
   - Both Python API and .NET React app will start automatically

## 🔧 Environment Variables

Create a `.env` file in the project root with:
```env
OPENAI_API_KEY=your_openai_key_here
OPENAI_API_BASE=https://your-azure-openai-endpoint/
OPENAI_API_VERSION=2024-12-01-preview
OPENAI_DEPLOYMENT_NAME=gpt-4o
```
