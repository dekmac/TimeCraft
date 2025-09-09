# TimeCraft Setup - Virtual Environment Support

This setup has been updated to work with Python virtual environments when conda is not available.

## 🚀 Quick Start

### Option 1: VS Code F5 (Recommended)
1. **Press F5** in VS Code
2. **Select "TimeCraft Full Stack"** from the dropdown
3. **Wait for environment setup** (runs automatically)
4. **Access the UI** at `http://localhost:8001/scenario-timeseries.html`

### Option 2: Manual Setup
```powershell
# Run the simple setup script
python setup_simple.py

# Or use the comprehensive setup (handles both conda and venv)
python setup_environment.py
```

### Option 3: Manual Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Install basic requirements
pip install fastapi uvicorn jinja2 aiofiles numpy pandas matplotlib scikit-learn

# Install BRIDGE requirements
pip install -r BRIDGE\requirements.txt

# Run the servers
python api_server.py  # API on port 8080
python serve.py       # Web UI on port 8001
```

## 🛠️ Setup Features

✅ **Automatic environment detection** (conda vs venv)  
✅ **Python virtual environment fallback**  
✅ **All dependencies installed automatically**  
✅ **BRIDGE text-to-timeseries support**  
✅ **FastAPI web server with CORS**  
✅ **VS Code F5 integration**  
✅ **Port conflict resolution**

## 🌐 Access Points

- **Web UI**: http://localhost:8001/scenario-timeseries.html
- **API Server**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

## 🔧 VS Code F5 Configurations

Available debug configurations:
- **TimeCraft Full Stack** - Both API and web servers
- **TimeCraft API Server** - Just the REST API  
- **TimeCraft Web Server** - Just the web interface
- **TimeCraft Training & Inference** - Main training script
- Component-specific options for TimeDP, BRIDGE, TarDiff, DiGA

## 📁 Virtual Environment

The setup creates a `venv` folder with:
- Python 3.11.9
- FastAPI and Uvicorn for web serving
- PyTorch for ML models
- NumPy, Pandas, Matplotlib for data processing
- All BRIDGE requirements for text-to-timeseries

## 🐛 Troubleshooting

- **Port conflicts**: Servers use ports 8080 (API) and 8001 (web)
- **Missing packages**: Run `pip install -r BRIDGE\requirements.txt` in venv
- **Environment issues**: Delete `venv` folder and re-run setup
- **Conda not found**: Setup automatically falls back to Python venv

## 🎯 What Works Now

- ✅ Environment setup without conda
- ✅ BRIDGE text-to-timeseries components  
- ✅ FastAPI REST API server
- ✅ Web interface with CORS support
- ✅ VS Code debugging and F5 support
- ✅ Automatic dependency management
