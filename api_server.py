#!/usr/bin/env python3
"""
TimeCraft REST API Server (Refactored)

This module provides a REST API interface for the TimeCraft time series generation framework.
It exposes key functionalities including text-to-time-series generation and multi-agent refinement.
"""

import os
import uvicorn
from typing import Dict
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import modules
from api.startup import (
    log_startup_environment, check_pandas_availability, 
    check_timecraft_components, ensure_fastapi_dependencies
)
from api.models import (
    HealthResponse, TextRefinementRequest, TextToTimeSeriesRequest,
    DomainPromptGenerationRequest, TargetAwareGenerationRequest,
    AggregateTimeSeriesRequest
)
from api.helpers import get_component_status
from api.file_handlers import (
    handle_generate_description, handle_analyze_csv
)
from api.text_handlers import (
    handle_refine_text
)
from api.timeseries_handlers import (
    handle_generate_timeseries_from_text, handle_domain_prompt_generation,
    handle_target_aware_generation, handle_aggregate_timeseries_generation
)

# Initialize components
log_startup_environment()
ensure_fastapi_dependencies()
HAS_PANDAS, HAS_NUMPY = check_pandas_availability()
COMPONENTS = check_timecraft_components()
COMPONENTS['HAS_PANDAS'] = HAS_PANDAS

# Create FastAPI app
app = FastAPI(
    title="TimeCraft API",
    description="REST API for TimeCraft time series generation framework",
    version="1.0.0",
    docs_url="/swagger"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "TimeCraft REST API",
        "version": "1.0.0",
        "documentation": "/swagger",
        "timecraft_available": str(COMPONENTS['TIMECRAFT_AVAILABLE']),
        "bridge_text_to_ts": str(COMPONENTS['BRIDGE_TEXT2TS_AVAILABLE']),
        "timedp_available": str(COMPONENTS['TIMEDP_AVAILABLE']),
        "tardiff_available": str(COMPONENTS['TARDIFF_AVAILABLE']),
        "pandas_available": str(HAS_PANDAS)
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", message="TimeCraft API is running")


@app.get("/status")
async def status():
    """Get system status and available components."""
    return JSONResponse(get_component_status(COMPONENTS))


@app.post("/generate-description")
async def generate_description(
    file: UploadFile = File(...),
    dataset_name: str = "uploaded_dataset",
    prediction_length: int = 168,
    llm_optimize: bool = False,
    openai_api_base: str = None,
    openai_api_version: str = None,
    openai_api_type: str = None
):
    """Generate textual descriptions for time series data."""
    return await handle_generate_description(
        file, dataset_name, prediction_length, llm_optimize,
        openai_api_base, openai_api_version, openai_api_type,
        COMPONENTS['TIMECRAFT_AVAILABLE'], HAS_PANDAS
    )


@app.post("/refine-text")
async def refine_text(request: TextRefinementRequest):
    """Refine textual descriptions using multi-agent approach."""
    return handle_refine_text(request, COMPONENTS['TIMECRAFT_AVAILABLE'])


@app.get("/models")
async def list_models():
    """List available models and their status."""
    models_status = {
        "BRIDGE - Text-to-Time-Series": {
            "available": COMPONENTS['BRIDGE_TEXT2TS_AVAILABLE'],
            "description": "Generate time series data from text descriptions",
            "endpoint": "/generate-timeseries-from-text"
        },
        "BRIDGE - Aggregate Multi-Tag Generation": {
            "available": COMPONENTS['BRIDGE_TEXT2TS_AVAILABLE'],
            "description": "Generate multiple time series for different tags from a single text description",
            "endpoint": "/generate-aggregate-timeseries"
        },
        "BRIDGE - Time-Series-to-Text": {
            "available": COMPONENTS['BRIDGE_AVAILABLE'],
            "description": "Generate text descriptions from time series data", 
            "endpoint": "/generate-description"
        },
        "TimeDP - Domain Prompts": {
            "available": COMPONENTS['TIMEDP_AVAILABLE'],
            "description": "Domain-specific time series generation using diffusion models",
            "endpoint": "/generate-timeseries-domain-prompt"
        },
        "TarDiff - Target-Aware Generation": {
            "available": COMPONENTS['TARDIFF_AVAILABLE'],
            "description": "Target-aware time series generation with classifier guidance",
            "endpoint": "/generate-timeseries-target-aware"
        }
    }
    
    return JSONResponse({
        "available_models": models_status,
        "overall_status": "Models available for inference" if any(m["available"] for m in models_status.values()) else "Demo mode - models not loaded"
    })


@app.post("/analyze-csv")
async def analyze_csv(file: UploadFile = File(...)):
    """Analyze uploaded CSV file and return basic statistics."""
    return handle_analyze_csv(file, HAS_PANDAS)


@app.post("/generate-timeseries-from-text")
async def generate_timeseries_from_text(request: TextToTimeSeriesRequest):
    """Generate time series data from text description using BRIDGE model."""
    return handle_generate_timeseries_from_text(request, COMPONENTS['BRIDGE_TEXT2TS_AVAILABLE'])


@app.post("/generate-timeseries-domain-prompt")
async def generate_timeseries_domain_prompt(request: DomainPromptGenerationRequest):
    """Generate time series data using TimeDP domain prompts."""
    return handle_domain_prompt_generation(request, COMPONENTS['TIMEDP_AVAILABLE'])


@app.post("/generate-timeseries-target-aware")
async def generate_timeseries_target_aware(request: TargetAwareGenerationRequest):
    """Generate time series data using TarDiff target-aware generation."""
    return handle_target_aware_generation(request, COMPONENTS['TARDIFF_AVAILABLE'])


@app.post("/generate-aggregate-timeseries")
async def generate_aggregate_timeseries(request: AggregateTimeSeriesRequest):
    """Generate multiple time series data for different tags based on a text description."""
    return handle_aggregate_timeseries_generation(request, COMPONENTS['BRIDGE_TEXT2TS_AVAILABLE'])


if __name__ == "__main__":
    # Set default environment variables
    os.environ.setdefault('DATA_ROOT', '/app/data')
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        reload=False,
        access_log=True
    )