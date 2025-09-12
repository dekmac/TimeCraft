"""
Anomaly generation handler for TimeCraft API.
"""

import numpy as np
from typing import List, Dict, Any
from api.models import AnomalyGenerationRequest, AnomalyGenerationResponse


def generate_anomaly_with_llm(
    existing_data: List[float],
    start_idx: int,
    end_idx: int,
    anomaly_type: str,
    severity: float = 1.0
) -> List[float]:
    """
    Generate anomaly data using algorithmic approaches (fallback when LLM is not available).
    
    Args:
        existing_data: The original time series data
        start_idx: Start index for anomaly injection
        end_idx: End index for anomaly injection
        anomaly_type: Type of anomaly ('spike', 'dip', 'drift', etc.)
        severity: Severity multiplier for the anomaly
    
    Returns:
        Modified time series with injected anomaly
    """
    data = np.array(existing_data.copy())
    
    # Extract the segment to modify
    segment = data[start_idx:end_idx + 1]
    baseline_mean = np.mean(segment)
    baseline_std = np.std(segment)
    
    # Generate anomaly based on type
    if anomaly_type == 'spike':
        # Sudden increase
        anomaly_values = segment + (baseline_std * 3 * severity)
        
    elif anomaly_type == 'dip':
        # Sudden decrease
        anomaly_values = segment - (baseline_std * 3 * severity)
        
    elif anomaly_type == 'drift':
        # Gradual change
        drift_slope = (baseline_std * 2 * severity) / len(segment)
        drift = np.arange(len(segment)) * drift_slope
        anomaly_values = segment + drift
        
    elif anomaly_type == 'noise':
        # Increased variability
        noise = np.random.normal(0, baseline_std * severity, len(segment))
        anomaly_values = segment + noise
        
    elif anomaly_type == 'flatline':
        # Constant value
        anomaly_values = np.full(len(segment), baseline_mean)
        
    elif anomaly_type == 'oscillation':
        # Unusual periodic behavior
        freq = 2 * np.pi / (len(segment) / 2)  # 2 cycles over the segment
        oscillation = np.sin(np.arange(len(segment)) * freq) * baseline_std * severity
        anomaly_values = segment + oscillation
        
    elif anomaly_type == 'outliers':
        # Scattered abnormal points
        anomaly_values = segment.copy()
        # Randomly select 20% of points to make outliers
        outlier_indices = np.random.choice(len(segment), size=max(1, len(segment) // 5), replace=False)
        for idx in outlier_indices:
            direction = np.random.choice([-1, 1])
            anomaly_values[idx] += direction * baseline_std * 2 * severity
    else:
        # Default to spike if unknown type
        anomaly_values = segment + (baseline_std * 3 * severity)
    
    # Replace the segment in the original data
    data[start_idx:end_idx + 1] = anomaly_values
    
    return data.tolist()


def handle_generate_anomaly(request: AnomalyGenerationRequest, has_llm: bool = False) -> Dict[str, Any]:
    """
    Handle anomaly generation request.
    
    Args:
        request: The anomaly generation request
        has_llm: Whether LLM components are available
    
    Returns:
        Response dictionary with generated anomaly data
    """
    try:
        # Validate request
        if not request.existing_timeseries:
            return {
                "success": False,
                "message": "Existing time series data is required",
                "tag_name": request.tag_name,
                "modified_timeseries": [],
                "anomaly_start_index": request.injection_start_index,
                "anomaly_end_index": request.injection_end_index,
                "anomaly_type": request.anomaly_type
            }
        
        if request.injection_start_index < 0 or request.injection_end_index >= len(request.existing_timeseries):
            return {
                "success": False,
                "message": "Invalid injection indices",
                "tag_name": request.tag_name,
                "modified_timeseries": [],
                "anomaly_start_index": request.injection_start_index,
                "anomaly_end_index": request.injection_end_index,
                "anomaly_type": request.anomaly_type
            }
        
        if request.injection_start_index > request.injection_end_index:
            return {
                "success": False,
                "message": "Start index must be less than or equal to end index",
                "tag_name": request.tag_name,
                "modified_timeseries": [],
                "anomaly_start_index": request.injection_start_index,
                "anomaly_end_index": request.injection_end_index,
                "anomaly_type": request.anomaly_type
            }
        
        # Generate the anomaly
        # For now, always use algorithmic approach regardless of LLM availability
        # In the future, you could implement LLM-based anomaly generation here
        modified_timeseries = generate_anomaly_with_llm(
            request.existing_timeseries,
            request.injection_start_index,
            request.injection_end_index,
            request.anomaly_type,
            request.severity
        )
        
        return {
            "success": True,
            "message": f"Successfully generated {request.anomaly_type} anomaly",
            "tag_name": request.tag_name,
            "modified_timeseries": modified_timeseries,
            "anomaly_start_index": request.injection_start_index,
            "anomaly_end_index": request.injection_end_index,
            "anomaly_type": request.anomaly_type
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error generating anomaly: {str(e)}",
            "tag_name": request.tag_name,
            "modified_timeseries": [],
            "anomaly_start_index": request.injection_start_index,
            "anomaly_end_index": request.injection_end_index,
            "anomaly_type": request.anomaly_type
        }
