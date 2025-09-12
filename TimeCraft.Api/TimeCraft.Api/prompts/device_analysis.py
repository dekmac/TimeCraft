"""
Device-specific prompt templates for TimeCraft API.

This module contains prompts for generating device-specific information and specifications.
"""


def create_device_analysis_prompt(tag_name: str, device_info: dict) -> str:
    """Create a prompt to ask the LLM to generate device-specific information."""
    return f"""You are an expert in industrial sensors and instrumentation. Analyze the sensor tag name "{tag_name}" and provide detailed specifications for realistic time series generation.

Based on the tag name, determine:
1. The sensor type and measurement principle
2. Typical operating ranges and units
3. Expected behavior patterns and characteristics
4. Noise levels and measurement precision
5. Environmental factors that affect readings
6. Industry-specific considerations

TAG NAME: {tag_name}
DETECTED SENSOR TYPE: {device_info.get('type', 'unknown')}
MEASUREMENT TYPE: {device_info.get('measurement', 'unknown')}
APPLICATION DOMAIN: {device_info.get('application', 'general industrial')}

Provide a comprehensive sensor specification block that includes:
- Typical measurement range
- Units of measurement
- Resolution/precision
- Expected behavior characteristics
- Environmental influences
- Typical patterns (daily cycles, trends, noise levels)
- Industry-specific considerations

Format as a detailed specification block starting with "DEVICE TYPE:" and including all relevant technical details for realistic time series generation."""


def create_basic_device_prompt(device_info: dict, tag_name: str) -> str:
    """Create a basic device prompt when LLM is not available."""
    return f"""
DEVICE TYPE: {device_info.get('type', 'sensor').title()} Sensor ({tag_name})
- Measurement: {device_info.get('measurement', 'process parameter')}
- Units: {device_info.get('units', 'various')}
- Typical Range: {device_info.get('typical_range', 'application dependent')}
- Application: {device_info.get('application', 'general industrial')}
- Generate realistic sensor data with appropriate noise, patterns, and behavior for this measurement type."""


def create_fallback_device_prompt(device_info: dict, tag_name: str) -> str:
    """Create a fallback device prompt with more details when LLM fails."""
    return f"""
DEVICE TYPE: {device_info.get('type', 'sensor').title()} Sensor ({tag_name})
- Measurement: {device_info.get('measurement', 'process parameter')}
- Units: {device_info.get('units', 'various')}
- Typical Range: {device_info.get('typical_range', 'application dependent')}
- Application: {device_info.get('application', 'general industrial')}
- Behavior: Generate realistic sensor data with appropriate noise, patterns, and behavior
- Environmental Effects: Consider temperature, humidity, and operational conditions
- Expected Patterns: Include natural variations, daily cycles, and measurement characteristics"""


def get_device_type_mapping() -> dict:
    """Get the mapping of keywords to device types for tag analysis."""
    return {
        'temperature': {
            'keywords': ['TEMP', 'TEMPERATURE', 'THERMAL'],
            'info': {
                'type': 'temperature',
                'measurement': 'temperature',
                'units': '°C or °F',
                'typical_range': '-40°C to +150°C'
            }
        },
        'pressure': {
            'keywords': ['PRESS', 'PRESSURE', 'VACUUM'],
            'info': {
                'type': 'pressure',
                'measurement': 'pressure',
                'units': 'kPa, bar, or psi',
                'typical_range': '0-1000 kPa'
            }
        },
        'flow': {
            'keywords': ['FLOW', 'FLOWRATE', 'VOLUMETRIC', 'MASS_FLOW'],
            'info': {
                'type': 'flow',
                'measurement': 'flow rate',
                'units': 'L/min, m³/h, or kg/h',
                'typical_range': '0-1000 L/min'
            }
        },
        'level': {
            'keywords': ['LEVEL', 'HEIGHT', 'DEPTH', 'TANK'],
            'info': {
                'type': 'level',
                'measurement': 'liquid/solid level',
                'units': 'mm, cm, or %',
                'typical_range': '0-100%'
            }
        },
        'speed': {
            'keywords': ['SPEED', 'RPM', 'VELOCITY', 'ROTATION'],
            'info': {
                'type': 'speed',
                'measurement': 'rotational or linear speed',
                'units': 'RPM, m/s, or Hz',
                'typical_range': '0-3600 RPM'
            }
        },
        'vibration': {
            'keywords': ['VIB', 'VIBRATION', 'ACCEL', 'ACCELEROMETER'],
            'info': {
                'type': 'vibration',
                'measurement': 'vibration/acceleration',
                'units': 'm/s², g, or mm/s',
                'typical_range': '±50g'
            }
        },
        'electrical': {
            'keywords': ['CURRENT', 'AMP', 'POWER', 'WATT', 'VOLTAGE', 'VOLT'],
            'info': {
                'type': 'electrical',
                'measurement': 'electrical parameter',
                'units': 'A, V, W, or kW',
                'typical_range': '0-1000A or 0-500V'
            }
        },
        'chemical': {
            'keywords': ['PH', 'CHEMICAL', 'CONCENTRATION', 'PPM', 'CONDUCTIVITY'],
            'info': {
                'type': 'chemical',
                'measurement': 'chemical property',
                'units': 'pH, ppm, or µS/cm',
                'typical_range': '0-14 pH or 0-1000 ppm'
            }
        },
        'humidity': {
            'keywords': ['HUMID', 'HUMIDITY', 'MOISTURE', 'RH'],
            'info': {
                'type': 'humidity',
                'measurement': 'relative humidity',
                'units': '% RH',
                'typical_range': '0-100% RH'
            }
        },
        'position': {
            'keywords': ['POS', 'POSITION', 'VALVE', 'ACTUATOR', 'DISPLACEMENT'],
            'info': {
                'type': 'position',
                'measurement': 'position/displacement',
                'units': 'mm, cm, or %',
                'typical_range': '0-100%'
            }
        }
    }


def get_application_domain_mapping() -> dict:
    """Get the mapping of keywords to application domains."""
    return {
        'dairy_processing': ['PASTEURIZER', 'HOMOGENIZER', 'MILK', 'DAIRY', 'CIP'],
        'chemical_processing': ['REACTOR', 'DISTILLATION', 'CATALYST', 'COLUMN'],
        'hvac_systems': ['CHILLER', 'AHU', 'HVAC', 'DAMPER', 'FAN'],
        'power_generation': ['GENERATOR', 'TURBINE', 'TRANSFORMER', 'GRID'],
        'water_treatment': ['PUMP', 'FILTER', 'CLARIFIER', 'EFFLUENT'],
        'automotive': ['ENGINE', 'BRAKE', 'TRANSMISSION', 'FUEL'],
        'manufacturing': ['MOTOR', 'CONVEYOR', 'HYDRAULIC', 'PRODUCTION'],
        'oil_gas': ['PIPELINE', 'CRUDE', 'REFINERY', 'COMPRESSOR']
    }