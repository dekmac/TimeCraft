#!/usr/bin/env python3
"""
Test the constraint-aware prompt generation without API calls.
"""

import sys
import os
sys.path.append("TimeCraft.Api/TimeCraft.Api")

from api.timeseries_handlers import extract_scenario_constraints

# Test scenario
description = """Generate synthetic time-series sensor data for monitoring a historic building (the Sagrada Família in Spain) during tourist season. The dataset should cover realistic readings. Note that the value ranges provided represent long-term seasonal variation; within a single day, values should only fluctuate within a smaller band, unless otherwise noted.

Include these sensor streams:

Temperature (°C): Long-term range 18–26 °C. For a single day, generate smooth curves within ±2 °C variance, with daytime slightly warmer than nighttime.
Humidity (%): Long-term range 40–70%. For a single day, values should stay mostly flat with only ±2–3% variation, as indoor humidity changes slowly.
Fissurometer (crack width, mm): Long-term range 0.5–2.0 mm. For a single day, keep values stable with only minimal jitter (±0.05 mm).
Occupancy (people): Range 0–60. Strong daily patterns: peak during morning tours (~10–12h) and afternoon (~14–16h), tapering off in the evening, near 0 overnight.
C02 levels.

Output as realistic, continuous time-series data with timestamps at hourly or sub-hourly resolution."""

def test_prompt_generation(tag_name, tag_unit):
    print(f"\n🏷️ Testing: {tag_name} ({tag_unit})")
    print("=" * 50)
    
    # Extract constraints
    constraints = extract_scenario_constraints(description, tag_name, tag_unit)
    
    # Build constraint-aware prompt section
    constraint_rules = ""
    if constraints['specific_rules']:
        constraint_rules = "\n".join([f"• {rule}" for rule in constraints['specific_rules']])
        constraint_rules = f"\nSPECIFIC CONSTRAINTS FOR {tag_name}:\n{constraint_rules}\n"
    
    print("📋 CONSTRAINT RULES THAT WILL BE ADDED TO PROMPT:")
    print(constraint_rules)
    
    print("✅ Range extracted:", f"{constraints['range_min']} - {constraints['range_max']} {tag_unit}")
    print("✅ Daily variation:", f"±{constraints['daily_variation']} {tag_unit}" if constraints['daily_variation'] else "None specified")

# Test the sensors that were problematic
print("🧪 Testing Constraint-Aware Prompt Generation")
print("=" * 60)

print("🔍 This will show the constraints that will be enforced in the LLM prompts")

test_prompt_generation("NAVE_TEMPERATURE_SENSOR_01", "°C")
test_prompt_generation("NAVE_CO2_SENSOR_01", "ppm")
test_prompt_generation("ENTRANCE_OCCUPANCY_SENSOR_01", "people")

print("\n✅ The prompts will now include these specific constraints!")
print("🎯 This should fix the issue where LLM was ignoring your scenario requirements.")
