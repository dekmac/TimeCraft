#!/usr/bin/env python3
"""
TimeCraft REST API Server (Demo Version)

This module provides a REST API for generating synthetic time series data based on
text descriptions. It's designed to demonstrate the capabilities of time series
generation from natural language descriptions.

Key Features:
- Text to time series generation
- Multiple pattern support (sine waves, linear trends, random walks)
- Realistic sensor data simulation
- CORS-enabled for web integration
"""

import os
import uvicorn
from typing import Dict
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Import modules
from api.startup import (
    log_startup_environment, check_pandas_availability, 
    check_timecraft_components, ensure_fastapi_dependencies
)
from api.models import (
    HealthResponse, TextRefinementRequest, TextToTimeSeriesRequest,
    DomainPromptGenerationRequest, TargetAwareGenerationRequest,
    AggregateTimeSeriesRequest, TagGenerationRequest, SingleTimeSeriesRequest
)
from api.helpers import get_component_status
from api.file_handlers import (
    handle_generate_description, handle_analyze_csv
)
from api.text_handlers import (
    handle_refine_text
)
from api.refine_prompt_models import RefinePromptRequest, RefinePromptResponse
from api.timeseries_handlers import (
    handle_generate_timeseries_from_text, handle_domain_prompt_generation,
    handle_target_aware_generation, handle_aggregate_timeseries_generation,
    handle_generate_tags, handle_generate_single_timeseries, refine_scenario_prompt
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
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def serve_ui():
    """Serve the TimeCraft UI."""
    return FileResponse("scenario-timeseries.html")


@app.get("/api", response_model=Dict[str, str])
async def api_root():
    """API root endpoint providing API information."""
    return {
        "message": "TimeCraft REST API",
        "version": "1.0.0",
        "mode": "demo"
    }

@app.get("/health")
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


@app.post("/refine-prompt", response_model=RefinePromptResponse)
async def refine_prompt(request: RefinePromptRequest):
    """Refine a scenario description into a structured, explicit prompt for timeseries generation."""
    refined = refine_scenario_prompt(request.scenario, request.sequence_length)
    return RefinePromptResponse(refined_prompt=refined)


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


@app.post("/generate-tags")
async def generate_tags(request: TagGenerationRequest):
    """Generate tag names from text description."""
    return handle_generate_tags(request, COMPONENTS['BRIDGE_TEXT2TS_AVAILABLE'])


@app.post("/generate-timeseries-for-tag") 
async def generate_timeseries_for_tag(request: SingleTimeSeriesRequest):
    """Generate timeseries data for a single tag."""
    return handle_generate_single_timeseries(request, COMPONENTS['BRIDGE_TEXT2TS_AVAILABLE'])


@app.post("/generate-aggregate-timeseries")
async def generate_aggregate_timeseries(request: AggregateTimeSeriesRequest):
    """
    Generate multiple time series based on a text description.
    
    This endpoint generates synthetic time series data that matches the scenario
    described in the text. It uses different patterns based on the type of
    sensor or measurement described.
    
    Args:
        request (AggregateTimeSeriesRequest): Request containing description and parameters
    
    Returns:
        dict: Generated time series data and metadata
    """
    try:
        # Generate appropriate tag names based on the description
        tag_names = generate_tag_names(request.text_description, request.num_tags)
        
        # Generate mock data for each tag
        timeseries_data = {}
        for tag in tag_names:
            if "temperature" in tag.lower():
                base_value = 25.0  # baseline temperature (°C)
                timeseries_data[tag] = generate_mock_timeseries(request.sequence_length, "sine", base_value)
            elif "pressure" in tag.lower():
                base_value = 100.0  # baseline pressure (kPa)
                timeseries_data[tag] = generate_mock_timeseries(request.sequence_length, "linear", base_value)
            else:
                timeseries_data[tag] = generate_mock_timeseries(request.sequence_length)

        return {
            "status": "success",
            "text_description": request.text_description,
            "tags": tag_names,
            "sequence_length": request.sequence_length,
            "aggregate_timeseries": timeseries_data,
            "timestamp": "2025-06-18T00:00:00Z"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)
