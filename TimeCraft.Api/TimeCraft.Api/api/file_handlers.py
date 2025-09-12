"""
File and CSV handling endpoints for TimeCraft API.
"""

import os
import tempfile
import traceback
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse

from .helpers import (
    setup_openai_config, create_demo_response, handle_api_error,
    validate_csv_file, create_temp_file, cleanup_temp_file
)


async def handle_generate_description(
    file: UploadFile, dataset_name: str, prediction_length: int,
    llm_optimize: bool, openai_api_base: str, openai_api_version: str,
    openai_api_type: str, timecraft_available: bool, has_pandas: bool
) -> JSONResponse:
    """Handle time series description generation."""
    try:
        validate_csv_file(file)
        
        if not timecraft_available:
            return create_demo_response(
                "demo_mode",
                "TimeCraft components not available. This is a demo response.",
                dataset_name=dataset_name,
                file_uploaded=file.filename,
                prediction_length=prediction_length,
                llm_optimize=llm_optimize,
                note="In production, this would generate actual time series descriptions"
            )
        
        # Process file
        content = await file.read()
        tmp_file_path = create_temp_file(content)
        
        try:
            setup_openai_config(openai_api_base, openai_api_version, openai_api_type)
            
            # Import TimeCraft modules
            from BRIDGE.run_inference import load_models, run_inference_from_dataframe
            import pandas as pd
            
            if not has_pandas:
                raise HTTPException(status_code=500, detail="pandas not available")
            
            # Load data
            try:
                df = pd.read_csv(tmp_file_path)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
            
            # Load models and run inference
            models = load_models()
            result = run_inference_from_dataframe(
                df, models, dataset_name, prediction_length,
                llm_optimize=llm_optimize
            )
            
            return JSONResponse({
                "status": "success",
                "dataset_name": dataset_name,
                "file_uploaded": file.filename,
                "prediction_length": prediction_length,
                "llm_optimize": llm_optimize,
                "description": result.get("description", "Generated description"),
                "details": result
            })
            
        finally:
            cleanup_temp_file(tmp_file_path)
            
    except Exception as e:
        return handle_api_error("generate_description", e)


async def handle_analyze_csv(file: UploadFile, has_pandas: bool) -> JSONResponse:
    """Analyze uploaded CSV file and return basic statistics."""
    try:
        validate_csv_file(file)
        
        if not has_pandas:
            return create_demo_response(
                "demo_mode",
                "pandas not available. This is a demo response showing mock CSV analysis.",
                filename=file.filename,
                columns=["timestamp", "value1", "value2", "value3"],
                rows=1000,
                statistics={"mean": 42.5, "std": 15.2, "min": 0.1, "max": 99.9},
                note="In production, this would analyze actual CSV data"
            )
        
        # Process file
        content = await file.read()
        tmp_file_path = create_temp_file(content)
        
        try:
            import pandas as pd
            
            # Load and analyze data
            df = pd.read_csv(tmp_file_path)
            
            analysis = {
                "filename": file.filename,
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "statistics": df.describe().to_dict() if len(df.select_dtypes(include='number').columns) > 0 else {}
            }
            
            return JSONResponse({
                "status": "success",
                "analysis": analysis
            })
            
        finally:
            cleanup_temp_file(tmp_file_path)
            
    except Exception as e:
        return handle_api_error("analyze_csv", e)