#!/usr/bin/env python3
"""
Lightweight TimeCraft API server for testing the enhanced workflow.
This version skips heavy ML dependencies and focuses on the core API functionality.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the essential API models and handlers
try:
    from api.models import (
        TagGenerationRequest,
        SingleTimeSeriesRequest,
        AggregateTimeSeriesRequest
    )
    from api.timeseries_handlers import (
        handle_generate_tags,
        handle_generate_single_timeseries,
        handle_aggregate_timeseries_generation
    )
    print("✅ Core TimeCraft API components imported successfully")
except ImportError as e:
    print(f"❌ Failed to import core components: {e}")
    sys.exit(1)

# Initialize the FastAPI app
app = FastAPI(
    title="TimeCraft API (Lightweight)",
    description="Enhanced TimeCraft API for testing workflow improvements",
    version="2.0.0-test"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock bridge availability for testing
BRIDGE_AVAILABLE = False

@app.get("/")
async def root():
    """Root endpoint."""
    return JSONResponse({
        "message": "TimeCraft API (Lightweight Test Version)",
        "version": "2.0.0-test",
        "status": "running",
        "note": "Enhanced workflow with units, scenario validation, and UI integration"
    })

@app.get("/health")
async def health():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "mode": "test",
        "bridge_available": BRIDGE_AVAILABLE,
        "enhanced_features": [
            "Tag generation with units",
            "Scenario-aware timeseries generation", 
            "Scenario validation",
            "Enhanced API responses with metadata"
        ]
    })

@app.post("/generate-tags")
async def generate_tags(request: TagGenerationRequest):
    """Generate tag names from text description with enhanced workflow."""
    try:
        print(f"🏷️ Generate tags called: {request.text_description}")
        response = handle_generate_tags(request, BRIDGE_AVAILABLE)
        print(f"✅ Tags generated successfully")
        return response
    except Exception as e:
        print(f"❌ Error in generate_tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-timeseries-for-tag")
async def generate_timeseries_for_tag(request: SingleTimeSeriesRequest):
    """Generate timeseries data for a single tag with enhanced workflow."""
    try:
        print(f"📊 Generate timeseries called for: {request.tag_name}")
        response = handle_generate_single_timeseries(request, BRIDGE_AVAILABLE)
        print(f"✅ Timeseries generated successfully for {request.tag_name}")
        return response
    except Exception as e:
        print(f"❌ Error in generate_timeseries_for_tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-aggregate-timeseries")
async def generate_aggregate_timeseries(request: AggregateTimeSeriesRequest):
    """Generate multiple time series data with enhanced workflow."""
    try:
        print(f"🚀 Generate aggregate timeseries called: {request.text_description}")
        response = handle_aggregate_timeseries_generation(request, BRIDGE_AVAILABLE)
        print(f"✅ Aggregate timeseries generated successfully")
        return response
    except Exception as e:
        print(f"❌ Error in generate_aggregate_timeseries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting TimeCraft API (Lightweight Test Server)")
    print("   Enhanced with units, scenario validation, and UI integration")
    print("   Running without heavy ML dependencies for testing")
    
    # Run the server
    uvicorn.run(
        "test_server:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level="info"
    )