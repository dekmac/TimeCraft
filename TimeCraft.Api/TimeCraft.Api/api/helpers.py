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
                           base_value: float = 1.0, context: dict = None) -> List[float]:
    """Generate realistic scenario-aware time series data."""
    import random
    
    # Analyze context for scenario-specific patterns
    if context is None:
        context = {}
    
    scenario_type = context.get("scenario_type", "general")
    sensor_type = context.get("sensor_type", "default")
    facility_type = context.get("facility_type", "industrial")
    
    # Time array (hours)
    time = np.linspace(0, length, length)
    
    # Generate scenario-specific patterns
    if scenario_type == "historic_building" or facility_type == "historic_building":
        return _generate_historic_building_pattern(length, pattern_type, base_value, sensor_type)
    elif scenario_type == "commercial" or facility_type == "commercial":
        return _generate_commercial_pattern(length, pattern_type, base_value, sensor_type)
    elif pattern_type == "sine":
        return _generate_sine_pattern(length, base_value, time)
    elif pattern_type == "linear":
        return _generate_linear_pattern(length, base_value, time)
    else:
        return _generate_default_pattern(length, base_value, time)


def _generate_historic_building_pattern(length: int, pattern_type: str, base_value: float, sensor_type: str) -> List[float]:
    """Generate patterns specific to historic building monitoring."""
    data = []
    
    # Determine sensor-specific baseline and behavior
    if "temp" in sensor_type.lower() or "hvac" in sensor_type.lower():
        # Temperature sensor in historic building
        base_temp = 20.0  # Target temperature
        for hour in range(length):
            hour_of_day = hour % 24
            day_of_week = (hour // 24) % 7
            
            # Daily visitor pattern (building open 9-17)
            if 9 <= hour_of_day <= 17:
                occupancy_factor = 1.0
                # Peak visitor hours (11-15)
                if 11 <= hour_of_day <= 15:
                    occupancy_factor = 1.5 if day_of_week < 5 else 2.0  # Higher on weekends
                visitor_heat = occupancy_factor * 2.0
            else:
                visitor_heat = 0.0
                
            # HVAC setback when closed
            if hour_of_day < 8 or hour_of_day > 18:
                setback = -3.0
            else:
                setback = 0.0
                
            # Daily thermal cycle
            thermal_cycle = 1.5 * np.sin(2 * np.pi * hour_of_day / 24 - np.pi/2)
            
            # Random noise
            noise = np.random.normal(0, 0.3)
            
            temp = base_temp + visitor_heat + setback + thermal_cycle + noise
            data.append(max(15.0, min(28.0, temp)))  # Realistic temperature bounds
            
    elif "humid" in sensor_type.lower():
        # Humidity sensor in historic building
        base_humidity = 55.0  # Target humidity for artifacts
        for hour in range(length):
            hour_of_day = hour % 24
            day_of_week = (hour // 24) % 7
            
            # Visitor humidity contribution
            if 9 <= hour_of_day <= 17:
                occupancy_factor = 1.0
                if 11 <= hour_of_day <= 15:
                    occupancy_factor = 1.5 if day_of_week < 5 else 2.5
                visitor_humidity = occupancy_factor * 8.0
            else:
                visitor_humidity = 0.0
                
            # Daily cycle
            daily_cycle = 5.0 * np.sin(2 * np.pi * hour_of_day / 24)
            
            # Weather influence (random)
            weather = np.random.normal(0, 3.0)
            noise = np.random.normal(0, 1.0)
            
            humidity = base_humidity + visitor_humidity + daily_cycle + weather + noise
            data.append(max(30.0, min(80.0, humidity)))  # Realistic humidity bounds
            
    elif "footfall" in sensor_type.lower() or "people" in sensor_type.lower():
        # Footfall counter in historic building
        for hour in range(length):
            hour_of_day = hour % 24
            day_of_week = (hour // 24) % 7
            
            if 9 <= hour_of_day <= 17:  # Open hours
                # Base visitor rate
                base_rate = 15 if day_of_week < 5 else 35  # Higher weekends
                
                # Peak hours multiplier
                if 11 <= hour_of_day <= 15:
                    peak_multiplier = 2.0
                elif 10 <= hour_of_day <= 16:
                    peak_multiplier = 1.5
                else:
                    peak_multiplier = 0.8
                    
                # Random variation
                random_factor = np.random.uniform(0.5, 1.5)
                
                footfall = base_rate * peak_multiplier * random_factor
                
                # Occasional special events (5% chance)
                if np.random.random() < 0.05:
                    footfall *= np.random.uniform(2.0, 4.0)
                    
            else:
                footfall = 0  # Closed hours
                
            data.append(max(0, int(footfall)))
            
    elif "vibration" in sensor_type.lower() or "seismic" in sensor_type.lower():
        # Structural vibration monitoring
        for hour in range(length):
            hour_of_day = hour % 24
            
            # Base structural vibration
            base_vibration = 0.15
            
            # Traffic influence (rush hours)
            if 7 <= hour_of_day <= 9 or 17 <= hour_of_day <= 19:
                traffic_factor = 2.0
            elif 22 <= hour_of_day or hour_of_day <= 6:
                traffic_factor = 0.3
            else:
                traffic_factor = 1.0
                
            # Visitor influence (minimal but present)
            if 9 <= hour_of_day <= 17:
                visitor_vibration = 0.02 * np.random.uniform(0.5, 1.5)
            else:
                visitor_vibration = 0.0
                
            # Wind effects
            wind_factor = 1.0 + 0.2 * np.sin(hour * 0.1) + np.random.uniform(-0.1, 0.1)
            
            # Measurement noise
            noise = np.random.normal(0, 0.01)
            
            vibration = base_vibration * traffic_factor * wind_factor + visitor_vibration + noise
            data.append(max(0.05, min(2.0, vibration)))
            
    else:
        # Generic sensor for historic building
        for hour in range(length):
            hour_of_day = hour % 24
            day_of_week = (hour // 24) % 7
            
            # Base operational pattern
            if 9 <= hour_of_day <= 17:
                operational_factor = 1.5 if day_of_week >= 5 else 1.0  # Higher weekends
            else:
                operational_factor = 0.3
                
            # Daily cycle
            daily_cycle = 0.2 * np.sin(2 * np.pi * hour_of_day / 24)
            
            # Random variation
            noise = np.random.normal(0, 0.1)
            
            value = base_value * operational_factor + daily_cycle + noise
            data.append(max(0, value))
            
    return data


def _generate_commercial_pattern(length: int, pattern_type: str, base_value: float, sensor_type: str) -> List[float]:
    """Generate patterns specific to commercial building monitoring."""
    data = []
    
    for hour in range(length):
        hour_of_day = hour % 24
        day_of_week = (hour // 24) % 7
        
        # Commercial building operational pattern
        if day_of_week < 5:  # Weekdays
            if 7 <= hour_of_day <= 18:
                operational_factor = 1.0
                if 9 <= hour_of_day <= 17:
                    operational_factor = 1.5  # Peak business hours
            else:
                operational_factor = 0.2
        else:  # Weekends
            operational_factor = 0.1
            
        # Daily cycle
        daily_cycle = 0.3 * np.sin(2 * np.pi * hour_of_day / 24)
        
        # Random variation
        noise = np.random.normal(0, 0.15)
        
        value = base_value * operational_factor + daily_cycle + noise
        data.append(max(0, value))
        
    return data


def _generate_sine_pattern(length: int, base_value: float, time: np.ndarray) -> List[float]:
    """Generate sine wave pattern for structural monitoring."""
    data = []
    for i, t in enumerate(time):
        # Primary structural resonance
        primary_freq = base_value * 0.01
        structural = 0.1 * np.sin(2 * np.pi * primary_freq * t / 24)
        
        # Daily environmental cycle
        daily_cycle = 0.05 * np.sin(2 * np.pi * t / 24)
        
        # Rush hour effects
        hour = t % 24
        rush_factor = 1.0
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            rush_factor = 1.5 + 0.3 * np.sin(2 * np.pi * (hour - 7) / 4)
        
        # Random vibrations
        noise = np.random.normal(0, 0.02)
        
        base_component = base_value * 0.001
        dynamic_component = (structural + daily_cycle) * rush_factor
        value = base_component + dynamic_component + noise
        data.append(max(0, value))
        
    return data


def _generate_linear_pattern(length: int, base_value: float, time: np.ndarray) -> List[float]:
    """Generate linear trend pattern for strain/displacement monitoring."""
    data = []
    base_strain = base_value * 0.1
    
    for i, t in enumerate(time):
        # Long-term trend
        long_term_trend = 0.01 * t / 24  # Per day
        
        # Daily thermal cycle
        thermal_cycle = 0.5 * np.sin(2 * np.pi * t / 24 - np.pi/4)
        
        # Load effects
        hour = t % 24
        load_effect = 0.0
        if 6 <= hour <= 22:
            sin_component = np.sin(2 * np.pi * (hour - 6) / 16)
            load_effect = 0.2 * (1 + 0.3 * sin_component)
        
        # Noise
        noise = np.random.normal(0, 0.05)
        
        value = base_strain + long_term_trend + thermal_cycle + load_effect + noise
        data.append(value)
        
    return data


def _generate_default_pattern(length: int, base_value: float, time: np.ndarray) -> List[float]:
    """Generate default mixed sensor pattern."""
    import random
    
    data = []
    base_pressure = base_value
    
    for i, t in enumerate(time):
        # Weather-driven variations
        weather_pattern = 2 * np.pi * t / 72 + random.random() * 2 * np.pi  # 3-day cycle
        weather_cycle = 0.2 * np.sin(weather_pattern)
        
        # Daily environmental effects
        daily_variation = 0.1 * np.sin(2 * np.pi * t / 24 + np.pi/6)
        
        # Random fluctuations
        random_noise = np.random.normal(0, 0.08)
        
        # Occasional events
        event_magnitude = 0.0
        if random.random() < 0.001:
            event_magnitude = np.random.normal(0, 0.5)
        
        value = base_pressure + weather_cycle + daily_variation + random_noise + event_magnitude
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
    """Parse LLM response to extract time series values with NO MOCK FALLBACKS.
    
    CRITICAL: This function will NEVER generate synthetic/mock data.
    If parsing fails or LLM is unavailable, returns empty list.
    """
    time_series_str = response.strip()
    if not time_series_str:
        print("⚠️ Empty LLM response; returning empty timeseries (no mock data)")
        return []
        
    if "Time Series:" in time_series_str:
        time_series_str = time_series_str.split("Time Series:")[-1].strip()
    
    # Convert to list of floats - NO MOCK FALLBACK
    try:
        time_series = [float(val.strip()) for val in time_series_str.split(',') if val.strip()]
    except ValueError as e:
        print(f"⚠️ LLM response parsing failed: {e}; returning empty timeseries (no mock data)")
        return []
    
    if not time_series:
        print("⚠️ No numeric values extracted from LLM response; returning empty timeseries (no mock data)")
        return []
    
    # Accept any length - truncate if longer, keep as-is if shorter (consistent with main parser)
    if len(time_series) > target_length:
        print(f"ℹ️ Parsed {len(time_series)} values; expected {target_length}. Truncating to expected length.")
        return time_series[:target_length]
    elif len(time_series) < target_length:
        print(f"ℹ️ Parsed {len(time_series)} (<{target_length}) values. Accepting short series without padding.")
    
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