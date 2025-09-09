"""
Helper functions for TimeCraft API operations.
"""

import os
import tempfile
import traceback
import numpy as np
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from fastapi.responses import JSONResponse


def setup_openai_config(openai_api_base: Optional[str] = None,
                       openai_api_version: Optional[str] = None,
                       openai_api_type: Optional[str] = None):
    """Set up OpenAI configuration from request parameters."""
    if openai_api_base:
        os.environ['OPENAI_API_BASE'] = openai_api_base
    if openai_api_version:
        os.environ['OPENAI_API_VERSION'] = openai_api_version
    if openai_api_type:
        os.environ['OPENAI_API_TYPE'] = openai_api_type


def create_demo_response(status: str, message: str, **kwargs) -> JSONResponse:
    """Create a standardized demo response."""
    response_data = {
        "status": status,
        "message": message,
        **kwargs
    }
    return JSONResponse(response_data)


def handle_api_error(operation: str, error: Exception) -> HTTPException:
    """Handle API errors with consistent logging and response format."""
    print(f"Error in {operation}: {traceback.format_exc()}")
    return HTTPException(status_code=500, detail=f"Internal server error: {str(error)}")


def validate_csv_file(file):
    """Validate that uploaded file is CSV."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")


def create_temp_file(content: bytes, suffix: str = '.csv') -> str:
    """Create temporary file and return path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode='wb') as tmp_file:
        tmp_file.write(content)
        return tmp_file.name


def cleanup_temp_file(file_path: str):
    """Safely clean up temporary file."""
    if os.path.exists(file_path):
        os.unlink(file_path)


def generate_mock_timeseries(length: int = 168, pattern_type: str = "default", 
                           base_value: float = 1.0) -> List[float]:
    """Generate realistic structural monitoring time series data."""
    import random
    
    # Time array (hours)
    time = np.linspace(0, length/24, length)  # Convert to days
    
    if pattern_type == "sine":
        # Multi-frequency structural vibration pattern
        # Primary structural mode + harmonics + environmental effects
        data = []
        for i, t in enumerate(time):
            # Primary structural resonance (0.5-2 Hz scaled to daily cycle)
            primary_freq = base_value * 0.01  # Scale base_value to frequency
            structural = 0.1 * np.sin(2 * np.pi * primary_freq * t)
            
            # Environmental daily cycle (temperature/traffic effects)
            daily_cycle = 0.05 * np.sin(2 * np.pi * t)  # 24-hour cycle
            
            # Traffic rush hour effects (higher amplitude 7-9am, 5-7pm)
            hour = (t * 24) % 24
            rush_factor = 1.0
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                rush_factor = 1.5 + 0.3 * np.sin(2 * np.pi * (hour - 7) / 4)
            
            # Random vibrations + measurement noise
            random_vibration = np.random.normal(0, 0.02)
            measurement_noise = np.random.normal(0, 0.005)
            
            # Combine all effects
            base_component = base_value * 0.001
            dynamic_component = (structural + daily_cycle) * rush_factor
            noise_component = random_vibration + measurement_noise
            value = base_component + dynamic_component + noise_component
            data.append(max(0, value))  # Ensure positive values
            
        return data
        
    elif pattern_type == "linear":
        # Strain gauge or displacement - shows trends + cycles
        data = []
        base_strain = base_value * 0.1  # Convert to microstrain scale
        
        for i, t in enumerate(time):
            # Long-term structural settlement/drift
            long_term_trend = 0.01 * t  # Gradual increase
            
            # Daily thermal expansion/contraction
            thermal_cycle = 0.5 * np.sin(2 * np.pi * t - np.pi/4)
            
            # Load effects (traffic, wind)
            hour = (t * 24) % 24
            load_effect = 0.0
            if 6 <= hour <= 22:  # Daytime activity
                sin_component = np.sin(2 * np.pi * (hour - 6) / 16)
                load_effect = 0.2 * (1 + 0.3 * sin_component)
            
            # Measurement noise and micro-vibrations
            noise = np.random.normal(0, 0.05)
            
            components = [base_strain, long_term_trend, thermal_cycle,
                          load_effect, noise]
            value = sum(components)
            data.append(value)
            
        return data
        
    else:
        # Default: Mixed sensor behavior (pressure, inclinometer, etc.)
        data = []
        base_pressure = base_value
        
        for i, t in enumerate(time):
            # Weather-driven variations (barometric pressure effects)
            weather_pattern = 2 * np.pi * t / 3 + random.random() * 2 * np.pi
            weather_cycle = 0.2 * np.sin(weather_pattern)
            
            # Daily environmental effects
            daily_variation = 0.1 * np.sin(2 * np.pi * t + np.pi/6)
            
            # Seasonal drift (very slow)
            seasonal_drift = 0.05 * np.sin(2 * np.pi * t / 365)
            
            # Random fluctuations
            random_noise = np.random.normal(0, 0.08)
            
            # Occasional events (structural events, maintenance, etc.)
            event_probability = 0.001  # Very rare
            event_magnitude = 0.0
            if random.random() < event_probability:
                event_magnitude = np.random.normal(0, 0.5)
            
            components = [base_pressure, weather_cycle, daily_variation,
                          seasonal_drift, random_noise, event_magnitude]
            value = sum(components)
            data.append(value)
            
        return data


def generate_mock_domain_series(domain_type: str, length: int, num_samples: int) -> List[List[float]]:
    """Generate mock time series based on domain type."""
    mock_series_batch = []
    for i in range(min(num_samples, 5)):  # Limit mock samples
        if domain_type.lower() == "finance":
            base_pattern = [100 + np.sin(j * 0.1) * 10 + np.random.normal(0, 2) for j in range(length)]
        elif domain_type.lower() == "energy":
            base_pattern = [50 + np.sin(j * 0.2) * 20 + np.random.normal(0, 3) for j in range(length)]
        else:
            base_pattern = [np.sin(j * 0.05) * 10 + np.random.normal(0, 1) for j in range(length)]
        mock_series_batch.append(base_pattern)
    return mock_series_batch


def generate_mock_target_aware_series(target_values: Optional[List[float]], 
                                    length: int, num_samples: int) -> List[List[float]]:
    """Generate mock target-aware time series."""
    mock_series_batch = []
    for i in range(min(num_samples, 5)):  # Limit mock samples
        if target_values:
            # Generate series that tends toward target values
            mock_series = []
            for j in range(length):
                if j < len(target_values):
                    # Blend toward target with some noise
                    target = target_values[j]
                    noise = np.random.normal(0, 0.1 * abs(target) if target != 0 else 0.1)
                    mock_series.append(target + noise)
                else:
                    # Extend pattern
                    mock_series.append(mock_series[-1] + np.random.normal(0, 0.1))
        else:
            # Generate generic series
            mock_series = [np.random.normal(0, 1) for _ in range(length)]
        mock_series_batch.append(mock_series)
    return mock_series_batch


def parse_llm_timeseries_response(response: str, target_length: int) -> List[float]:
    """Parse LLM response to extract time series values."""
    time_series_str = response.strip()
    if "Time Series:" in time_series_str:
        time_series_str = time_series_str.split("Time Series:")[-1].strip()
    
    # Convert to list of floats
    try:
        time_series = [float(val.strip()) for val in time_series_str.split(',') if val.strip()]
    except ValueError:
        # If parsing fails, generate a simple mock series
        time_series = [float(i % 10 + 1) for i in range(target_length)]
    
    # Ensure we have exactly target_length points
    if len(time_series) < target_length:
        # Extend by repeating the pattern
        while len(time_series) < target_length:
            time_series.extend(time_series[:min(len(time_series), target_length - len(time_series))])
    elif len(time_series) > target_length:
        time_series = time_series[:target_length]
    
    return time_series


def get_component_status(components: Dict[str, bool]) -> Dict[str, Any]:
    """Get comprehensive component status information."""
    return {
        "status": "running",
        "components": {
            "timecraft_bridge": components['BRIDGE_AVAILABLE'],
            "bridge_text_to_ts": components['BRIDGE_TEXT2TS_AVAILABLE'],
            "timedp": components['TIMEDP_AVAILABLE'],
            "tardiff": components['TARDIFF_AVAILABLE'],
            "pandas": components.get('HAS_PANDAS', False),
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
    }


def generate_tag_names_from_description(description: str, num_tags: int) -> List[str]:
    """Generate tag names based on text description using keyword mapping."""
    # Simple tag generation based on common keywords
    keywordMapping = {
        'temperature': ['Temperature_Sensor_1', 'Temperature_Sensor_2', 'Ambient_Temperature'],
        'pressure': ['Pressure_Gauge_1', 'Pressure_Gauge_2', 'System_Pressure'],
        'vibration': ['Vibration_X', 'Vibration_Y', 'Vibration_Z'],
        'factory': ['Production_Rate', 'Machine_Efficiency', 'Power_Consumption'],
        'energy': ['Power_Output', 'Voltage', 'Current'],
        'sensor': ['Sensor_A', 'Sensor_B', 'Sensor_C'],
        'monitoring': ['CPU_Usage', 'Memory_Usage', 'Network_Traffic'],
        'financial': ['Stock_Price', 'Trading_Volume', 'Market_Index'],
        'weather': ['Temperature', 'Humidity', 'Wind_Speed'],
        'traffic': ['Vehicle_Count', 'Speed_Average', 'Congestion_Level'],
        'smart': ['Smart_Meter_1', 'Smart_Meter_2', 'Smart_Device'],
        'building': ['HVAC_Temperature', 'Occupancy_Rate', 'Lighting_Level'],
        'hvac': ['HVAC_Temperature', 'Humidity_Control', 'Air_Flow'],
        'flow': ['Flow_Rate_1', 'Flow_Rate_2', 'Flow_Sensor'],
        'machine': ['Machine_1_Status', 'Machine_2_Status', 'Machine_Efficiency'],
        'production': ['Production_Rate', 'Quality_Score', 'Downtime'],
        'iot': ['IoT_Sensor_1', 'IoT_Sensor_2', 'IoT_Gateway'],
        'network': ['Network_Latency', 'Bandwidth_Usage', 'Packet_Loss']
    }

    tags = []
    lower_description = description.lower()
    
    # Find matching keywords and generate appropriate tags
    for keyword, tag_list in keywordMapping.items():
        if keyword in lower_description:
            tags.extend(tag_list)
            if len(tags) >= num_tags:
                break

    # Fill remaining slots with generic tags
    while len(tags) < num_tags:
        tags.append(f'Tag_{len(tags) + 1}')

    return tags[:num_tags]