#!/usr/bin/env python3
"""
Test the new streamlined timeseries prompt
"""

# Mock the time horizon
class MockTimeHorizon:
    def __init__(self):
        self.period = 24
        self.unit = 'hours'
        self.granularity = 'minute'

def get_sensor_specific_guidance(tag_name: str, tag_unit: str, time_horizon=None, sequence_length: int = 288) -> str:
    """Generate focused, sensor-specific guidance for realistic timeseries generation."""
    
    # Time context
    if time_horizon:
        duration = f"{time_horizon.period} {time_horizon.unit}"
        frequency = f"every {time_horizon.granularity}"
        time_info = f"TIMESPAN: {duration} ({sequence_length} measurements {frequency})"
    else:
        time_info = f"MEASUREMENTS: {sequence_length} sequential data points"
    
    # Determine sensor type from name
    tag_lower = tag_name.lower()
    
    if 'temp' in tag_lower:
        patterns = """
TEMPERATURE PATTERNS:
• Daily cycle: Cool night (18-20°C) → gradual morning rise → peak afternoon (24-26°C) → gradual fall
• SMOOTH curves only - NO zigzag, sawtooth, or multiple peaks
• Changes: 0.1-0.3°C per minute, 0.5-2°C per hour maximum
• Thermal mass prevents rapid temperature swings"""
        
    elif 'humidity' in tag_lower:
        patterns = """
HUMIDITY PATTERNS:
• Daily cycle: Peak early morning (60-65%) → minimum afternoon (45-50%) → rise evening
• NATURAL fluctuations with micro-variations (±0.1-0.3%)
• AVOID linear sequences (45.2, 45.3, 45.4...) - humidity varies naturally
• Changes: 1-3% per minute, 5-15% per hour maximum"""
        
    elif 'occupancy' in tag_lower or 'count' in tag_lower:
        patterns = """
OCCUPANCY PATTERNS:
• Daily cycle: Low overnight (1-3 people) → morning rise → peak tours (10-30 people) → evening decline
• Tour groups create periodic spikes every 30-60 minutes during peak hours
• AVOID all zeros - even at night there should be occasional security/maintenance staff
• Realistic range: 0-60 people with clear daily patterns"""
        
    elif 'co2' in tag_lower:
        patterns = """
CO2 PATTERNS:
• Baseline: 400-450 ppm (outdoor level)
• Occupied periods: Rise to 600-1200 ppm depending on crowding and ventilation
• Daily cycle follows occupancy with 15-30 minute lag due to air mixing
• Changes: 5-20 ppm per minute, 50-300 ppm per hour"""
        
    elif 'crack' in tag_lower or 'width' in tag_lower:
        patterns = """
CRACK WIDTH PATTERNS:
• Very stable measurements with minimal variation (±0.01-0.05 mm)
• Slow thermal expansion/contraction over day (±0.1 mm maximum)
• Small random sensor noise (±0.001-0.005 mm)
• AVOID constant values - include micro-variations from thermal effects"""
        
    else:
        patterns = f"""
GENERAL SENSOR PATTERNS:
• Include natural variations appropriate for {tag_name}
• Follow realistic physics for {tag_unit} measurements
• Avoid constant values, linear sequences, or unrealistic patterns"""
    
    return f"""{time_info}

{patterns}

CRITICAL RULES:
• NO constant values (all identical numbers)
• NO linear progressions (1.0, 1.1, 1.2, 1.3...)
• NO unrealistic patterns (zigzag, sawtooth, random spikes)
• Include natural micro-variations even in stable conditions"""

def test_new_prompts():
    """Test the new streamlined prompts for different sensor types."""
    
    time_horizon = MockTimeHorizon()
    scenario = "Generate synthetic time-series sensor data for monitoring a historic building (the Sagrada Família in Spain) during tourist season."
    
    test_sensors = [
        ("SF_SAGRADA_MAINHALL_TEMP_01", "°C"),
        ("SF_SAGRADA_MAINHALL_HUMIDITY_01", "%"),
        ("SF_SAGRADA_MAINHALL_OCCUPANCY_01", "people"),
        ("SF_SAGRADA_TOWER_CRACKWIDTH_01", "mm"),
        ("SF_SAGRADA_MAINHALL_CO2_01", "ppm")
    ]
    
    for tag_name, tag_unit in test_sensors:
        print(f"\n{'='*80}")
        print(f"PROMPT FOR: {tag_name}")
        print(f"{'='*80}")
        
        sensor_guidance = get_sensor_specific_guidance(tag_name, tag_unit, time_horizon, 288)
        
        enhanced_prompt = f"""Generate 288 realistic sensor values for: {tag_name} ({tag_unit})

SCENARIO: {scenario}

{sensor_guidance}

OUTPUT FORMAT:
Your response must be ONLY comma-separated numbers. Start with a number, not text.

CORRECT: 23.4, 24.1, 23.8, 24.5, 23.9, 24.2
WRONG: DEVICE TYPE: Temperature Sensor
WRONG: Values: 23.4, 24.1, 23.8"""
        
        print(enhanced_prompt)
        print(f"\n{'='*80}")
        print(f"PROMPT LENGTH: {len(enhanced_prompt)} characters")
        print(f"{'='*80}")

if __name__ == "__main__":
    test_new_prompts()