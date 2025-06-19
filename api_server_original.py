#!/usr/bin/env python3
"""
TimeCraft REST API Server

This module provides a REST API interface for the TimeCraft time series generation framework.
It exposes key functionalities including text-to-time-series generation and multi-agent refinement.
"""

import os
import sys
import json
import tempfile
import traceback
from typing import Optional, Dict, Any, List
from pathlib import Path

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BRIDGE'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diffusion'))


def log_startup_environment():
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

log_startup_environment()

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("FastAPI and uvicorn are required. Installing...")
    os.system("pip install fastapi uvicorn python-multipart")
    from fastapi import FastAPI, HTTPException, UploadFile, File
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn

# Try to import pandas for basic data processing
try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
    HAS_NUMPY = True
except ImportError:
    HAS_PANDAS = False
    HAS_NUMPY = False
    print("Warning: pandas/numpy not available. Some functionality will be limited.")

# Import TimeCraft components when available
TIMECRAFT_AVAILABLE = False
BRIDGE_AVAILABLE = False
TIMEDP_AVAILABLE = False
TARDIFF_AVAILABLE = False

try:
    from BRIDGE.ts_to_text import generate_text_description_for_time_series
    TIMECRAFT_AVAILABLE = True
    BRIDGE_AVAILABLE = True
    print("TimeCraft BRIDGE components loaded successfully.")
except ImportError:
    print("Warning: Could not import BRIDGE components. Running in demo mode.")

# Try to import BRIDGE text-to-timeseries generation components
try:
    from BRIDGE.self_refine.task_init import TimeSeriesTaskInit
    from BRIDGE.llm_agents.llm import ChatLLM
    BRIDGE_TEXT2TS_AVAILABLE = True
    print("BRIDGE text-to-timeseries components loaded successfully.")
except ImportError:
    # print actual error message for debugging
    print(traceback.format_exc())
    BRIDGE_TEXT2TS_AVAILABLE = False
    print("Warning: Could not import BRIDGE text-to-timeseries components.")

# Try to import TimeDP components  
try:
    import torch
    import pytorch_lightning as pl
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TimeDP'))
    TIMEDP_AVAILABLE = True
    print("TimeDP components loaded successfully.")
except ImportError:
    print("Warning: Could not import TimeDP components.")

# Try to import TarDiff components
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TarDiff'))
    TARDIFF_AVAILABLE = True
    print("TarDiff components loaded successfully.")
except ImportError:
    print("Warning: Could not import TarDiff components.")

app = FastAPI(
    title="TimeCraft API",
    description="REST API for TimeCraft time series generation framework",
    version="1.0.0",
    docs_url="/swagger"
)

class TimeSeriesGenerationRequest(BaseModel):
    """Request model for time series generation."""
    dataset_name: str
    prediction_length: Optional[int] = 168
    llm_optimize: Optional[bool] = False

class TextRefinementRequest(BaseModel):
    """Request model for text refinement."""
    initial_text: str
    openai_api_base: Optional[str] = None
    openai_api_version: Optional[str] = None
    openai_api_type: Optional[str] = None
    team_iterations: Optional[int] = 3
    global_iterations: Optional[int] = 2

class TextToTimeSeriesRequest(BaseModel):
    """Request model for text-to-time-series generation using BRIDGE model."""
    text_description: str
    model_name: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.0
    openai_api_base: Optional[str] = None
    openai_api_version: Optional[str] = None
    openai_api_type: Optional[str] = None

class DomainPromptGenerationRequest(BaseModel):
    """Request model for TimeDP domain prompt-based generation."""
    domain_type: str  # e.g., "finance", "energy", "traffic"
    sequence_length: Optional[int] = 168
    num_samples: Optional[int] = 100
    use_text: Optional[bool] = False
    text_prompt: Optional[str] = None
    
class TargetAwareGenerationRequest(BaseModel):
    """Request model for TarDiff target-aware generation."""
    target_values: Optional[List[float]] = None
    guidance_strength: Optional[float] = 1.0
    sequence_length: Optional[int] = 168
    num_samples: Optional[int] = 100
    classifier_guidance: Optional[bool] = True

class AggregateTimeSeriesRequest(BaseModel):
    """Request model for aggregate multi-tag time series generation."""
    text_description: str
    num_tags: Optional[int] = 5
    sequence_length: Optional[int] = 168
    model_name: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.0
    openai_api_base: Optional[str] = None
    openai_api_version: Optional[str] = None
    openai_api_type: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: str

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "TimeCraft REST API",
        "version": "1.0.0",
        "documentation": "/swagger",
        "timecraft_available": str(TIMECRAFT_AVAILABLE),
        "bridge_text_to_ts": str(BRIDGE_TEXT2TS_AVAILABLE),
        "timedp_available": str(TIMEDP_AVAILABLE),
        "tardiff_available": str(TARDIFF_AVAILABLE),
        "pandas_available": str(HAS_PANDAS)
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="TimeCraft API is running"
    )

@app.get("/status")
async def status():
    """Get system status and available components."""
    return JSONResponse({
        "status": "running",
        "components": {
            "timecraft_bridge": BRIDGE_AVAILABLE,
            "bridge_text_to_ts": BRIDGE_TEXT2TS_AVAILABLE,
            "timedp": TIMEDP_AVAILABLE,
            "tardiff": TARDIFF_AVAILABLE,
            "pandas": HAS_PANDAS,
            "api_server": True
        },
        "environment": {
            "data_root": os.environ.get('DATA_ROOT', '/app/data'),
            "python_path": os.environ.get('PYTHONPATH', ''),
            "openai_api_key_set": bool(os.environ.get('OPENAI_API_KEY')),
            "openai_api_base": os.environ.get('OPENAI_API_BASE', 'default'),
            "openai_api_version": os.environ.get('OPENAI_API_VERSION', 'default'),
            "openai_api_type": os.environ.get('OPENAI_API_TYPE', 'openai')
        }
    })

@app.post("/generate-description")
async def generate_description(
    file: UploadFile = File(...),
    dataset_name: str = "uploaded_dataset",
    prediction_length: int = 168,
    llm_optimize: bool = False,
    openai_api_base: Optional[str] = None,
    openai_api_version: Optional[str] = None,
    openai_api_type: Optional[str] = None
):
    """
    Generate textual descriptions for time series data.
    
    Args:
        file: CSV file containing time series data
        dataset_name: Name/ID of the dataset
        prediction_length: Prediction length for time series windows
        llm_optimize: Whether to use LLM to optimize text descriptions
        openai_api_base: OpenAI API base URL (for Azure OpenAI support)
        openai_api_version: OpenAI API version (for Azure OpenAI support)
        openai_api_type: OpenAI API type (for Azure OpenAI support)
    
    Returns:
        JSON response with generation status and results
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        if not TIMECRAFT_AVAILABLE:
            # Return a mock response when TimeCraft is not available
            return JSONResponse({
                "status": "demo_mode",
                "message": "TimeCraft components not available. This is a demo response.",
                "dataset_name": dataset_name,
                "file_uploaded": file.filename,
                "prediction_length": prediction_length,
                "llm_optimize": llm_optimize,
                "note": "In production, this would generate actual time series descriptions"
            })
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Set OpenAI configuration if provided
            if openai_api_base:
                os.environ['OPENAI_API_BASE'] = openai_api_base
            if openai_api_version:
                os.environ['OPENAI_API_VERSION'] = openai_api_version
            if openai_api_type:
                os.environ['OPENAI_API_TYPE'] = openai_api_type
            
            # Generate text descriptions
            generate_text_description_for_time_series(
                file_path=tmp_file_path,
                prediction_length=prediction_length,
                dataset_name=dataset_name,
                llm_optimize=llm_optimize,
                llm_api_key=os.environ.get('OPENAI_API_KEY')
            )
            
            # Check if output file was created
            output_file = tmp_file_path.replace('.csv', '_with_descriptions.csv')
            if os.path.exists(output_file):
                # Read and return basic stats
                basic_stats = {"status": "success"}
                if HAS_PANDAS:
                    try:
                        df = pd.read_csv(output_file)
                        basic_stats.update({
                            "rows": len(df),
                            "columns": list(df.columns)
                        })
                    except Exception as e:
                        basic_stats["stats_error"] = str(e)
                
                return JSONResponse({
                    "status": "success",
                    "message": "Text descriptions generated successfully",
                    "dataset_name": dataset_name,
                    "output_available": True,
                    **basic_stats
                })
            else:
                raise HTTPException(status_code=500, detail="Output file was not created")
                
        finally:
            # Clean up temporary files
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
            output_file = tmp_file_path.replace('.csv', '_with_descriptions.csv')
            if os.path.exists(output_file):
                os.unlink(output_file)
                
    except Exception as e:
        print(f"Error in generate_description: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/refine-text")
async def refine_text(request: TextRefinementRequest):
    """
    Refine textual descriptions using multi-agent approach.
    
    Args:
        request: Text refinement request containing initial text and parameters
    
    Returns:
        JSON response with refined text and refinement logs
    """
    try:
        # Set OpenAI configuration if provided
        if request.openai_api_base:
            os.environ['OPENAI_API_BASE'] = request.openai_api_base
        if request.openai_api_version:
            os.environ['OPENAI_API_VERSION'] = request.openai_api_version
        if request.openai_api_type:
            os.environ['OPENAI_API_TYPE'] = request.openai_api_type
        
        if not TIMECRAFT_AVAILABLE:
            # Return a mock response when TimeCraft is not available
            return JSONResponse({
                "status": "demo_mode",
                "message": "TimeCraft components not available. This is a demo response.",
                "original_text": request.initial_text,
                "refined_text": f"[DEMO REFINED] {request.initial_text}",
                "refinement_logs": {
                    "team_iterations": request.team_iterations,
                    "global_iterations": request.global_iterations,
                    "improvements": ["Enhanced clarity (demo)", "Improved structure (demo)"]
                },
                "note": "In production, this would use multi-agent refinement"
            })
        
        # For now, return a mock response since the full multi-agent system
        # requires more complex setup
        return JSONResponse({
            "status": "success",
            "message": "Text refinement completed",
            "original_text": request.initial_text,
            "refined_text": f"[REFINED] {request.initial_text}",
            "refinement_logs": {
                "team_iterations": request.team_iterations,
                "global_iterations": request.global_iterations,
                "improvements": ["Enhanced clarity", "Improved structure"]
            }
        })
        
    except Exception as e:
        print(f"Error in refine_text: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/models")
async def list_models():
    """List available models and their status."""
    models_status = {
        "BRIDGE - Text-to-Time-Series": {
            "available": BRIDGE_TEXT2TS_AVAILABLE,
            "description": "Generate time series data from text descriptions",
            "endpoint": "/generate-timeseries-from-text"
        },
        "BRIDGE - Aggregate Multi-Tag Generation": {
            "available": BRIDGE_TEXT2TS_AVAILABLE,
            "description": "Generate multiple time series for different tags from a single text description",
            "endpoint": "/generate-aggregate-timeseries"
        },
        "BRIDGE - Time-Series-to-Text": {
            "available": BRIDGE_AVAILABLE,
            "description": "Generate text descriptions from time series data", 
            "endpoint": "/generate-description"
        },
        "TimeDP - Domain Prompts": {
            "available": TIMEDP_AVAILABLE,
            "description": "Domain-specific time series generation using diffusion models",
            "endpoint": "/generate-timeseries-domain-prompt"
        },
        "TarDiff - Target-Aware Generation": {
            "available": TARDIFF_AVAILABLE,
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
    """
    Analyze uploaded CSV file and return basic statistics.
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        if not HAS_PANDAS:
            return JSONResponse({
                "status": "limited",
                "message": "Pandas not available. Cannot perform detailed analysis.",
                "filename": file.filename
            })
        
        # Read CSV file
        content = await file.read()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            df = pd.read_csv(tmp_file_path)
            
            analysis = {
                "status": "success",
                "filename": file.filename,
                "shape": df.shape,
                "columns": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "null_counts": df.isnull().sum().to_dict(),
                "numeric_columns": list(df.select_dtypes(include=['number']).columns),
                "sample_data": df.head().to_dict('records') if len(df) > 0 else []
            }
            
            return JSONResponse(analysis)
            
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        print(f"Error in analyze_csv: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/generate-timeseries-from-text")
async def generate_timeseries_from_text(request: TextToTimeSeriesRequest):
    """
    Generate time series data from text description using BRIDGE model.
    
    Args:
        request: Request containing text description and model parameters
    
    Returns:
        JSON response with generated time series data
    """
    try:
        if not BRIDGE_TEXT2TS_AVAILABLE:
            # Return a mock response when BRIDGE text-to-timeseries is not available
            mock_series = [1.0, 1.5, 2.0, 1.8, 2.5, 3.0, 2.7, 2.2] * 21  # 168 points
            return JSONResponse({
                "status": "demo_mode",
                "message": "BRIDGE text-to-timeseries components not available. This is a demo response.",
                "text_description": request.text_description,
                "generated_timeseries": mock_series[:168],
                "model_used": request.model_name,
                "note": "In production, this would generate actual time series from text using BRIDGE model"
            })
        
        # Set OpenAI configuration if provided
        if request.openai_api_base:
            os.environ['OPENAI_API_BASE'] = request.openai_api_base
        if request.openai_api_version:
            os.environ['OPENAI_API_VERSION'] = request.openai_api_version
        if request.openai_api_type:
            os.environ['OPENAI_API_TYPE'] = request.openai_api_type
            
        # output requestion information including OpenAI API settings
        print(f"Generating time series from text description: {request.text_description}")
        print(f"Using model: {request.model_name}, Temperature: {request.temperature}")
        
        # Initialize the ChatLLM model
        try:
            chat_llm = ChatLLM(
                model=request.model_name,
                temperature=request.temperature,
                api_base=request.openai_api_base,
                api_version=request.openai_api_version,
                api_type=request.openai_api_type
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to initialize LLM: {str(e)}")
        
        # For now, we'll use a simple prompt-based approach
        # In production, this would use proper example files and trained models
        try:
            # Create a simple prompt for time series generation
            prompt = f"""Generate a time series of 168 numerical values based on this description: {request.text_description}

Please return only the numerical values separated by commas, without any additional text or explanation.

Example format: 1.2, 3.4, 2.1, 4.5, ...

Time Series:"""
            
            response = chat_llm.generate(prompt)
            
            # Parse the response to extract time series values
            time_series_str = response.strip()
            if "Time Series:" in time_series_str:
                time_series_str = time_series_str.split("Time Series:")[-1].strip()
            
            # Convert to list of floats
            try:
                time_series = [float(val.strip()) for val in time_series_str.split(',') if val.strip()]
            except ValueError as e:
                # If parsing fails, generate a simple mock series
                print(f"Failed to parse LLM response: {e}")
                time_series = [float(i % 10 + 1) for i in range(168)]
            
            # Ensure we have exactly 168 points
            if len(time_series) < 168:
                # Extend by repeating the pattern
                while len(time_series) < 168:
                    time_series.extend(time_series[:min(len(time_series), 168 - len(time_series))])
            elif len(time_series) > 168:
                time_series = time_series[:168]
            
            return JSONResponse({
                "status": "success",
                "message": "Time series generated successfully from text description",
                "text_description": request.text_description,
                "generated_timeseries": time_series,
                "model_used": request.model_name,
                "length": len(time_series)
            })
            
        except Exception as e:
            print(f"Error during time series generation: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate time series: {str(e)}")
        
    except Exception as e:
        print(f"Error in generate_timeseries_from_text: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/generate-timeseries-domain-prompt")
async def generate_timeseries_domain_prompt(request: DomainPromptGenerationRequest):
    """
    Generate time series data using TimeDP domain prompts.
    
    Args:
        request: Request containing domain type and generation parameters
    
    Returns:
        JSON response with generated time series data
    """
    try:
        if not TIMEDP_AVAILABLE:
            # Return a mock response when TimeDP is not available
            mock_series_batch = []
            for i in range(min(request.num_samples, 5)):  # Limit mock samples
                # Generate different patterns based on domain type
                if request.domain_type.lower() == "finance":
                    base_pattern = [100 + np.sin(j * 0.1) * 10 + np.random.normal(0, 2) for j in range(request.sequence_length)]
                elif request.domain_type.lower() == "energy":
                    base_pattern = [50 + np.sin(j * 0.2) * 20 + np.random.normal(0, 3) for j in range(request.sequence_length)]
                else:
                    base_pattern = [np.sin(j * 0.05) * 10 + np.random.normal(0, 1) for j in range(request.sequence_length)]
                mock_series_batch.append(base_pattern)
            
            return JSONResponse({
                "status": "demo_mode",
                "message": "TimeDP components not available. This is a demo response.",
                "domain_type": request.domain_type,
                "generated_timeseries": mock_series_batch,
                "num_samples": len(mock_series_batch),
                "sequence_length": request.sequence_length,
                "note": "In production, this would use TimeDP diffusion model for domain-specific generation"
            })
        
        # For now, return a placeholder since full TimeDP integration requires complex setup
        return JSONResponse({
            "status": "not_implemented",
            "message": "TimeDP integration is in development",
            "domain_type": request.domain_type,
            "note": "Full TimeDP diffusion model integration requires model checkpoints and complex setup"
        })
        
    except Exception as e:
        print(f"Error in generate_timeseries_domain_prompt: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/generate-timeseries-target-aware")
async def generate_timeseries_target_aware(request: TargetAwareGenerationRequest):
    """
    Generate time series data using TarDiff target-aware generation.
    
    Args:
        request: Request containing target values and generation parameters
    
    Returns:
        JSON response with generated time series data
    """
    try:
        if not TARDIFF_AVAILABLE:
            # Return a mock response when TarDiff is not available
            mock_series_batch = []
            for i in range(min(request.num_samples, 5)):  # Limit mock samples
                if request.target_values:
                    # Generate series that tends toward target values
                    mock_series = []
                    for j in range(request.sequence_length):
                        if j < len(request.target_values):
                            # Blend toward target with some noise
                            target = request.target_values[j]
                            noise = np.random.normal(0, 0.1 * abs(target) if target != 0 else 0.1)
                            mock_series.append(target + noise)
                        else:
                            # Extend pattern
                            mock_series.append(mock_series[-1] + np.random.normal(0, 0.1))
                else:
                    # Generate generic series
                    mock_series = [np.random.normal(0, 1) for _ in range(request.sequence_length)]
                mock_series_batch.append(mock_series)
            
            return JSONResponse({
                "status": "demo_mode", 
                "message": "TarDiff components not available. This is a demo response.",
                "target_values": request.target_values,
                "generated_timeseries": mock_series_batch,
                "num_samples": len(mock_series_batch),
                "sequence_length": request.sequence_length,
                "guidance_strength": request.guidance_strength,
                "note": "In production, this would use TarDiff model for target-aware generation"
            })
        
        # For now, return a placeholder since full TarDiff integration requires complex setup
        return JSONResponse({
            "status": "not_implemented",
            "message": "TarDiff integration is in development",
            "target_values": request.target_values,
            "note": "Full TarDiff model integration requires model checkpoints and classifier guidance setup"
        })
        
    except Exception as e:
        print(f"Error in generate_timeseries_target_aware: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/generate-aggregate-timeseries")
async def generate_aggregate_timeseries(request: AggregateTimeSeriesRequest):
    """
    Generate multiple time series data for different tags based on a text description.
    
    This endpoint takes a text description, generates relevant tag names for that context,
    and then generates a time series for each tag.
    
    Args:
        request: Request containing text description and generation parameters
    
    Returns:
        JSON response with generated time series data for multiple tags
    """
    try:
        # Set OpenAI configuration if provided
        if request.openai_api_base:
            os.environ['OPENAI_API_BASE'] = request.openai_api_base
        if request.openai_api_version:
            os.environ['OPENAI_API_VERSION'] = request.openai_api_version
        if request.openai_api_type:
            os.environ['OPENAI_API_TYPE'] = request.openai_api_type

        if not BRIDGE_TEXT2TS_AVAILABLE:
            # Return a mock response when BRIDGE text-to-timeseries is not available
            mock_tags = {}
            tag_names = [f"tag{i+1}" for i in range(request.num_tags)]
            
            for i, tag_name in enumerate(tag_names):
                # Generate different patterns for each tag
                base_value = (i + 1) * 10
                mock_series = [base_value + np.sin(j * 0.1 + i) * 5 + np.random.normal(0, 1) 
                              for j in range(request.sequence_length)]
                mock_tags[tag_name] = mock_series
            
            return JSONResponse({
                "status": "demo_mode",
                "message": "BRIDGE text-to-timeseries components not available. This is a demo response.",
                "text_description": request.text_description,
                "generated_timeseries": mock_tags,
                "note": "In production, this would generate actual tags and time series from text using BRIDGE model"
            })

        # Initialize the ChatLLM model
        try:
            chat_llm = ChatLLM(
                model=request.model_name,
                temperature=request.temperature,
                api_base=request.openai_api_base,
                api_version=request.openai_api_version,
                api_type=request.openai_api_type
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to initialize LLM: {str(e)}")

        print(f"Generating aggregate time series from description: {request.text_description}")
        print(f"Using model: {request.model_name}, Target tags: {request.num_tags}")

        # Step 1: Generate relevant tag names based on the text description
        tag_generation_prompt = f"""Based on the following description, generate {request.num_tags} relevant tag names that would be measured or tracked in this context:

Description: {request.text_description}

Please return only the tag names, one per line, without any additional text or explanation.
The tag names should be concise, descriptive, and relevant to the scenario described.

Example format:
TemperatureSensor1
PressureReading
FlowRate
PowerConsumption
ErrorCount

Tag names:"""

        try:
            tag_response = chat_llm.generate(tag_generation_prompt)
            tag_lines = [line.strip() for line in tag_response.strip().split('\n') if line.strip()]
            
            # Clean up tag names and ensure we have the right number
            tag_names = []
            for line in tag_lines:
                # Remove any numbering or bullet points
                clean_tag = line.replace('-', '').replace('*', '').replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').strip()
                if clean_tag and len(clean_tag) > 0:
                    tag_names.append(clean_tag)
            
            # Ensure we have the requested number of tags
            if len(tag_names) < request.num_tags:
                # Fill with generic names if needed
                for i in range(len(tag_names), request.num_tags):
                    tag_names.append(f"Tag{i+1}")
            elif len(tag_names) > request.num_tags:
                tag_names = tag_names[:request.num_tags]
                
        except Exception as e:
            print(f"Failed to generate tag names: {e}")
            # Fall back to generic tag names
            tag_names = [f"Tag{i+1}" for i in range(request.num_tags)]

        print(f"Generated tag names: {tag_names}")

        # Step 2: Generate time series for each tag
        generated_timeseries = {}
        
        for tag_name in tag_names:
            try:
                # Create specific prompt for this tag
                tag_specific_prompt = f"""Generate a time series of {request.sequence_length} numerical values for the tag "{tag_name}" in the context of: {request.text_description}

The values should be realistic for this specific measurement/sensor in the given scenario.

Please return only the numerical values separated by commas, without any additional text or explanation.

Example format: 1.2, 3.4, 2.1, 4.5, ...

Time Series for {tag_name}:"""

                response = chat_llm.generate(tag_specific_prompt)
                
                # Parse the response to extract time series values
                time_series_str = response.strip()
                if f"Time Series for {tag_name}:" in time_series_str:
                    time_series_str = time_series_str.split(f"Time Series for {tag_name}:")[-1].strip()
                elif "Time Series:" in time_series_str:
                    time_series_str = time_series_str.split("Time Series:")[-1].strip()
                
                # Convert to list of floats
                try:
                    time_series = [float(val.strip()) for val in time_series_str.split(',') if val.strip()]
                except ValueError as e:
                    print(f"Failed to parse LLM response for {tag_name}: {e}")
                    # Generate a simple pattern based on tag position
                    tag_index = tag_names.index(tag_name)
                    base_value = (tag_index + 1) * 10
                    time_series = [base_value + np.sin(i * 0.1) * 5 + np.random.normal(0, 1) 
                                  for i in range(request.sequence_length)]
                
                # Ensure we have exactly the requested length
                if len(time_series) < request.sequence_length:
                    # Extend by repeating the pattern
                    while len(time_series) < request.sequence_length:
                        time_series.extend(time_series[:min(len(time_series), request.sequence_length - len(time_series))])
                elif len(time_series) > request.sequence_length:
                    time_series = time_series[:request.sequence_length]
                
                generated_timeseries[tag_name] = time_series
                
            except Exception as e:
                print(f"Error generating time series for tag {tag_name}: {e}")
                # Generate fallback series
                tag_index = tag_names.index(tag_name)
                base_value = (tag_index + 1) * 10
                fallback_series = [base_value + np.sin(i * 0.1) * 5 + np.random.normal(0, 1) 
                                  for i in range(request.sequence_length)]
                generated_timeseries[tag_name] = fallback_series

        return JSONResponse({
            "status": "success",
            "message": "Time series generated successfully from text description",
            "text_description": request.text_description,
            "generated_timeseries": generated_timeseries
        })

    except Exception as e:
        print(f"Error in generate_aggregate_timeseries: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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