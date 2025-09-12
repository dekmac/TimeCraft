"""
Startup and component availability checks for TimeCraft API.
"""

import os
import sys
import traceback

# Add project root to Python path
# We're in TimeCraft.Api/TimeCraft.Api/api/startup.py
# ML components are in TimeCraft.Api/ (three levels up)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'BRIDGE'))
sys.path.append(os.path.join(project_root, 'diffusion'))


def log_startup_environment():
    """Log startup environment information."""
    print("==== TimeCraft API Server Startup ====")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("Environment variables:")
    for key, value in os.environ.items():
        if "KEY" in key.upper() or "SECRET" in key.upper() or "TOKEN" in key.upper() or "PASSWORD" in key.upper():
            print(f"  {key}: [REDACTED]")
        else:
            print(f"  {key}: {value}")
    print("======================================")


def check_pandas_availability():
    """Check if pandas and numpy are available."""
    try:
        import pandas as pd
        import numpy as np
        return True, True
    except ImportError:
        print("Warning: pandas/numpy not available. Some functionality will be limited.")
        return False, False


def check_timecraft_components():
    """Check availability of TimeCraft components."""
    component_status = {
        'TIMECRAFT_AVAILABLE': False,
        'BRIDGE_AVAILABLE': False,
        'BRIDGE_TEXT2TS_AVAILABLE': False,
        'TIMEDP_AVAILABLE': False,
        'TARDIFF_AVAILABLE': False
    }
    
    # Try to import BRIDGE components
    try:
        from BRIDGE.ts_to_text import generate_text_description_for_time_series
        component_status['TIMECRAFT_AVAILABLE'] = True
        component_status['BRIDGE_AVAILABLE'] = True
        print("TimeCraft BRIDGE components loaded successfully.")
    except ImportError:
        print("Warning: Could not import BRIDGE components. Running in demo mode.")

    # Try to import BRIDGE text-to-timeseries generation components
    try:
        from BRIDGE.self_refine.task_init import TimeSeriesTaskInit
        from BRIDGE.llm_agents.llm import ChatLLM
        component_status['BRIDGE_TEXT2TS_AVAILABLE'] = True
        print("BRIDGE text-to-timeseries components loaded successfully.")
    except ImportError:
        print(traceback.format_exc())
        print("Warning: Could not import BRIDGE text-to-timeseries components.")

    # Try to import TimeDP components  
    try:
        import torch
        import pytorch_lightning as pl
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'TimeDP'))
        component_status['TIMEDP_AVAILABLE'] = True
        print("TimeDP components loaded successfully.")
    except ImportError:
        print("Warning: Could not import TimeDP components.")

    # Try to import TarDiff components
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'TarDiff'))
        component_status['TARDIFF_AVAILABLE'] = True
        print("TarDiff components loaded successfully.")
    except ImportError:
        print("Warning: Could not import TarDiff components.")
    
    return component_status


def ensure_fastapi_dependencies():
    """Ensure FastAPI and uvicorn are available."""
    try:
        from fastapi import FastAPI, HTTPException, UploadFile, File
        from fastapi.responses import JSONResponse
        from pydantic import BaseModel
        import uvicorn
        return True
    except ImportError:
        print("FastAPI and uvicorn are required. Installing...")
        os.system("pip install fastapi uvicorn python-multipart")
        try:
            from fastapi import FastAPI, HTTPException, UploadFile, File
            from fastapi.responses import JSONResponse
            from pydantic import BaseModel
            import uvicorn
            return True
        except ImportError:
            return False