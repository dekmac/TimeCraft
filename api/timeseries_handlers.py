"""
Time series generation endpoints for TimeCraft API.
"""

from fastapi.responses import JSONResponse
from .models import (
    TextToTimeSeriesRequest, DomainPromptGenerationRequest, 
    TargetAwareGenerationRequest, AggregateTimeSeriesRequest
)
from .helpers import (
    create_demo_response, handle_api_error, generate_mock_timeseries,
    generate_mock_domain_series, generate_mock_target_aware_series,
    parse_llm_timeseries_response
)


def generate_tag_names_from_description(description: str, num_tags: int) -> list:
    """Generate appropriate tag names based on description keywords."""
    keywords_to_tags = {
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
        'smart': ['Smart_Device_1', 'Smart_Device_2', 'Smart_Device_3'],
        'building': ['HVAC_Temperature', 'Occupancy_Count', 'Light_Level'],
        'iot': ['IoT_Device_1', 'IoT_Device_2', 'IoT_Device_3']
    }
    
    tags = []
    lower_desc = description.lower()
    
    # Find matching keywords and add their tags
    for keyword, tag_list in keywords_to_tags.items():
        if keyword in lower_desc:
            tags.extend(tag_list)
            if len(tags) >= num_tags:
                break
    
    # Fill remaining slots with generic tags
    while len(tags) < num_tags:
        tags.append(f'Tag_{len(tags) + 1}')
    
    return tags[:num_tags]


def handle_generate_timeseries_from_text(request: TextToTimeSeriesRequest, bridge_text2ts_available: bool) -> JSONResponse:
    """Generate time series data from text description using BRIDGE model."""
    try:
        if not bridge_text2ts_available:
            mock_data = generate_mock_timeseries(
                request.length, 
                request.text, 
                getattr(request, 'frequency', 'hourly')
            )
            return create_demo_response(
                "demo_mode",
                "BRIDGE Text2TS model not available. This is a demo response with mock time series data.",
                **mock_data
            )
        
        # Import BRIDGE modules
        from BRIDGE.inference.text_to_timeseries import generate_timeseries_from_text
        
        # Generate time series
        result = generate_timeseries_from_text(
            text=request.text,
            length=request.length,
            frequency=getattr(request, 'frequency', 'hourly'),
            domain=getattr(request, 'domain', None)
        )
        
        return JSONResponse({
            "status": "success",
            "text": request.text,
            "length": request.length,
            "frequency": getattr(request, 'frequency', 'hourly'),
            "timeseries": result.get("timeseries", []),
            "metadata": result.get("metadata", {}),
            "details": result
        })
        
    except Exception as e:
        return handle_api_error("generate_timeseries_from_text", e)


def handle_domain_prompt_generation(request: DomainPromptGenerationRequest, timedp_available: bool) -> JSONResponse:
    """Generate time series data using TimeDP domain prompts."""
    try:
        if not timedp_available:
            mock_data = generate_mock_domain_series(request.domain, request.length)
            return create_demo_response(
                "demo_mode", 
                "TimeDP model not available. This is a demo response with mock domain-specific time series.",
                **mock_data
            )
        
        # Import TimeDP modules
        from TimeDP.inference.domain_generation import generate_with_domain_prompt
        
        # Generate time series with domain prompts
        result = generate_with_domain_prompt(
            domain=request.domain,
            length=request.length,
            num_samples=getattr(request, 'num_samples', 1)
        )
        
        return JSONResponse({
            "status": "success", 
            "domain": request.domain,
            "length": request.length,
            "num_samples": getattr(request, 'num_samples', 1),
            "timeseries": result.get("timeseries", []),
            "details": result
        })
        
    except Exception as e:
        return handle_api_error("domain_prompt_generation", e)


def handle_target_aware_generation(request: TargetAwareGenerationRequest, tardiff_available: bool) -> JSONResponse:
    """Generate time series data using TarDiff target-aware generation."""
    try:
        if not tardiff_available:
            mock_data = generate_mock_target_aware_series(
                request.target_value, 
                request.length,
                getattr(request, 'guidance_scale', 1.0)
            )
            return create_demo_response(
                "demo_mode",
                "TarDiff model not available. This is a demo response with mock target-aware time series.",
                **mock_data
            )
        
        # Import TarDiff modules  
        from TarDiff.inference.target_aware_generation import generate_target_aware_timeseries
        
        # Generate target-aware time series
        result = generate_target_aware_timeseries(
            target_value=request.target_value,
            length=request.length,
            guidance_scale=getattr(request, 'guidance_scale', 1.0),
            num_samples=getattr(request, 'num_samples', 1)
        )
        
        return JSONResponse({
            "status": "success",
            "target_value": request.target_value, 
            "length": request.length,
            "guidance_scale": getattr(request, 'guidance_scale', 1.0),
            "num_samples": getattr(request, 'num_samples', 1),
            "timeseries": result.get("timeseries", []),
            "details": result
        })
        
    except Exception as e:
        return handle_api_error("target_aware_generation", e)


def handle_aggregate_timeseries_generation(request: AggregateTimeSeriesRequest, bridge_text2ts_available: bool) -> JSONResponse:
    """Generate multiple time series data for different tags based on a text description."""
    try:
        if not bridge_text2ts_available:
            # Generate tag names based on scenario
            tags = generate_tag_names_from_description(request.text_description, request.num_tags)
            
            # Generate mock data for each tag
            mock_results = {}
            for i, tag in enumerate(tags):
                mock_data = generate_mock_timeseries(
                    request.sequence_length,
                    "sine" if i % 3 == 0 else "linear" if i % 3 == 1 else "default",
                    50.0 + i * 20
                )
                mock_results[tag] = mock_data
            
            return create_demo_response(
                "demo_mode",
                "BRIDGE Text2TS model not available. This is a demo response with mock aggregate time series data.",
                text_description=request.text_description,
                tags=tags,
                num_tags=request.num_tags,
                sequence_length=request.sequence_length,
                aggregate_timeseries=mock_results,
                note="In production, this would generate actual multi-tag time series"
            )
        
        # Generate tag names based on scenario  
        tags = generate_tag_names_from_description(request.text_description, request.num_tags)
        
        # Import BRIDGE modules
        from BRIDGE.inference.text_to_timeseries import generate_aggregate_timeseries
        
        # Generate aggregate time series
        result = generate_aggregate_timeseries(
            text=request.text_description,
            tags=tags,
            length=request.sequence_length,
            frequency='hourly',
            domain=getattr(request, 'domain', None)
        )
        
        # Parse LLM response if available
        if 'llm_response' in result:
            parsed_response = parse_llm_timeseries_response(result['llm_response'])
            result.update(parsed_response)
        
        return JSONResponse({
            "status": "success",
            "text_description": request.text_description,
            "tags": tags,
            "num_tags": request.num_tags,
            "sequence_length": request.sequence_length,
            "aggregate_timeseries": result.get("aggregate_timeseries", {}),
            "metadata": result.get("metadata", {}),
            "details": result
        })
        
    except Exception as e:
        return handle_api_error("aggregate_timeseries_generation", e)