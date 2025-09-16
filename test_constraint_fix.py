#!/usr/bin/env python3
"""
Test the fixed timeseries generation with proper constraints.
"""

import sys
import os
sys.path.append("TimeCraft.Api/TimeCraft.Api")

# Set environment variables for testing
os.environ['TIMESERIES_STRICT_LENGTH'] = 'false'
os.environ['TIMESERIES_ENABLE_AUTO_IMPROVE'] = 'true'

from api.timeseries_handlers import generate_timeseries_with_llm, FallbackChatLLM
from api.models import TimeHorizon

# Test scenario
description = """Generate synthetic time-series sensor data for monitoring a historic building (the Sagrada Família in Spain) during tourist season. The dataset should cover realistic readings. Note that the value ranges provided represent long-term seasonal variation; within a single day, values should only fluctuate within a smaller band, unless otherwise noted.

Include these sensor streams:

Temperature (°C): Long-term range 18–26 °C. For a single day, generate smooth curves within ±2 °C variance, with daytime slightly warmer than nighttime.
Humidity (%): Long-term range 40–70%. For a single day, values should stay mostly flat with only ±2–3% variation, as indoor humidity changes slowly.
Fissurometer (crack width, mm): Long-term range 0.5–2.0 mm. For a single day, keep values stable with only minimal jitter (±0.05 mm).
Occupancy (people): Range 0–60. Strong daily patterns: peak during morning tours (~10–12h) and afternoon (~14–16h), tapering off in the evening, near 0 overnight.
C02 levels.

Output as realistic, continuous time-series data with timestamps at hourly or sub-hourly resolution."""

# Create time horizon
time_horizon = TimeHorizon(
    period=24,
    unit='hours',
    granularity='minute',
    total_points=288
)

print("🧪 Testing Constraint-Aware Timeseries Generation")
print("=" * 60)

# Test temperature sensor
print(f"\n🌡️ Testing Temperature Sensor")
print(f"Expected: 18-26°C range, ±2°C daily variation, smooth curves")

try:
    # Create LLM (this might fail if no API key)
    chat_llm = FallbackChatLLM('gpt-4o', temperature=0.7)
    
    result = generate_timeseries_with_llm(
        tag_name="NAVE_TEMPERATURE_SENSOR_01",
        description=description,
        sequence_length=20,  # Small test
        tag_index=0,
        chat_llm=chat_llm,
        tag_unit="°C",
        time_horizon=time_horizon
    )
    
    values = result.get('values', [])
    if values:
        print(f"✅ Generated {len(values)} values")
        print(f"   Range: {min(values):.2f}°C to {max(values):.2f}°C")
        print(f"   First 10: {[f'{v:.1f}' for v in values[:10]]}")
        
        # Check constraints
        if min(values) >= 18 and max(values) <= 26:
            print(f"   ✅ RANGE CHECK: Within 18-26°C bounds")
        else:
            print(f"   ❌ RANGE CHECK: Outside 18-26°C bounds!")
            
        # Check daily variation (for small sample, check if reasonable)
        value_range = max(values) - min(values)
        if value_range <= 4:  # ±2°C = 4°C total range
            print(f"   ✅ VARIATION CHECK: {value_range:.1f}°C range is reasonable")
        else:
            print(f"   ❌ VARIATION CHECK: {value_range:.1f}°C range too large!")
    else:
        print(f"   ❌ No values generated")
        
except Exception as e:
    print(f"   ⚠️ Test failed (probably no API key): {e}")

print(f"\n📊 Test complete - check if constraints are being enforced in prompts")