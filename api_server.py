#!/usr/bin/env python3
"""
TimeCraft REST API Server

This module provides a REST API interface for the TimeCraft time series generation framework.
It exposes key functionalities including text-to-time-series generation and multi-agent refinement.
"""

import os
import sys
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import API components
from api.startup import log_startup_environment, check_timecraft_components, ensure_fastapi_dependencies, check_pandas_availability
from api.models import (
    AggregateTimeSeriesRequest, TextToTimeSeriesRequest, 
    DomainPromptGenerationRequest, TargetAwareGenerationRequest
)
from api.timeseries_handlers import (
    handle_aggregate_timeseries_generation, handle_generate_timeseries_from_text,
    handle_domain_prompt_generation, handle_target_aware_generation
)
from api.file_handlers import handle_analyze_csv

# Set up startup environment
log_startup_environment()

# Ensure dependencies are available
if not ensure_fastapi_dependencies():
    raise ImportError("Could not import FastAPI dependencies")

# Check component availability
COMPONENTS = check_timecraft_components()
HAS_PANDAS, HAS_NUMPY = check_pandas_availability()

# Create FastAPI app

app = FastAPI(
    title="TimeCraft API",
    description="REST API for TimeCraft time series generation",
    version="1.0.0"
)

# Configure CORS for web interface integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "TimeCraft REST API",
        "version": "1.0.0",
        "components": COMPONENTS
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring API status."""
    return {
        "status": "healthy",
        "message": "TimeCraft API is running",
        "components": COMPONENTS
    }

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


@app.post("/analyze-csv")
async def analyze_csv(file: UploadFile = File(...)):
    """Analyze uploaded CSV file and return basic statistics."""
    return handle_analyze_csv(file, HAS_PANDAS)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)
