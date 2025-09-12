# TimeCraft.Api

Python FastAPI backend for the TimeCraft time series generation framework.

## Project Structure

```
TimeCraft.Api/
├── TimeCraft.Api/           # Main API application
│   ├── main.py             # FastAPI application entry point (was api_server.py)
│   ├── api/                # API modules
│   │   ├── startup.py      # Environment setup and component checks
│   │   ├── models.py       # Pydantic data models
│   │   ├── handlers/       # Request handlers organized by feature
│   │   ├── helpers.py      # Utility functions
│   │   └── ...
│   └── requirements.txt    # Python dependencies
├── scripts/                # Setup and utility scripts
│   ├── setup_simple.py     # Basic Python environment setup
│   ├── setup_environment.py # Advanced environment setup
│   └── serve.py            # Alternative server launcher
├── tests/                  # Test files
│   ├── test_*.py          # Various API tests
│   └── ...
├── training/               # ML training scripts
│   └── train_inference.py # Training and inference utilities
├── BRIDGE/                 # Text-to-timeseries ML model
├── TarDiff/               # Target-aware diffusion model
├── TimeDP/                # Time series diffusion model  
├── DiGA/                  # DiGA model
├── diffusion/             # Base diffusion components
└── process/               # Data processing utilities
```

## Quick Start

1. **Set up the environment:**
   ```bash
   cd TimeCraft.Api
   python scripts/setup_simple.py
   ```

2. **Activate the virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate.bat
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install additional dependencies:**
   ```bash
   pip install -r TimeCraft.Api/requirements.txt
   ```

4. **Run the API server:**
   ```bash
   python TimeCraft.Api/main.py
   ```

5. **Access the API:**
   - Web UI: http://localhost:8080
   - API docs: http://localhost:8080/swagger
   - Health check: http://localhost:8080/health

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_api_functional.py
```

### API Development

The main FastAPI application is in `TimeCraft.Api/main.py`. API routes and handlers are organized in the `api/` directory.

### ML Components

The ML models (BRIDGE, TarDiff, TimeDP, DiGA, diffusion) are kept at the project root level to maintain import compatibility with existing code.

## Docker Support

The API can be containerized. Make sure Docker files reference the new structure:

```dockerfile
# Update Dockerfile to use TimeCraft.Api/TimeCraft.Api/main.py as entry point
```

## Migration Notes

This structure was migrated from the original flat structure where Python files were scattered in the project root. Key changes:

- `api_server.py` → `TimeCraft.Api/TimeCraft.Api/main.py`
- `api/` → `TimeCraft.Api/TimeCraft.Api/api/`
- Setup scripts → `TimeCraft.Api/scripts/`
- Test files → `TimeCraft.Api/tests/`
- ML components moved to `TimeCraft.Api/` but kept at same relative level

## Dependencies

See `requirements.txt` for the full list. Key dependencies:
- FastAPI: Web framework
- Uvicorn: ASGI server
- Pydantic: Data validation
- NumPy/Pandas: Data processing
- Various ML libraries for the TimeCraft models
