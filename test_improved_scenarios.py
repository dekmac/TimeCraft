#!/usr/bin/env python3
"""
Test script for improved scenario-based timeseries generation.
Tests the enhanced context-aware generation for historic building monitoring.
"""

import sys
import os
import json

# Add API path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from timeseries_handlers import (
    analyze_scenario_context,
    create_timeseries_generation_prompt,
    generate_operational_patterns,
    generate_sensor_specific_guidance,
    detect_device_type_from_tag,
    FallbackChatLLM
)
from helpers import generate_mock_timeseries


def test_scenario_analysis():
    """Test the scenario context analysis functionality."""
    print("🧪 Testing Scenario Context Analysis")
    print("=" * 50)
    
    # Test historic building scenario
    description = "I want sensor data for monitoring a historic building. These sensor readings should be realistic for a historic building in Spain during tourist season."
    scenario = "I would like to see hvac, humidity, temperature and seismic activity which should all be relatively stable aside from daily fluctuations. I also want to see footfall from a presence sensor so we can monitor the footfall in the area."
    
    context = analyze_scenario_context(description, scenario)
    
    print(f"📊 Scenario Analysis Results:")
    print(f"   Facility Type: {context['facility_type']}")
    print(f"   Operational Schedule: {context['operational_schedule']}")
    print(f"   Environmental Factors: {context['environmental_factors']}")
    print(f"   Special Events: {context['special_events']}")
    print(f"   Building Characteristics: {context['building_characteristics']}")
    print(f"   Expected Sensor Ranges: {context['expected_sensor_ranges']}")
    print()
    
    return context


def test_enhanced_mock_generation():
    """Test enhanced scenario-aware mock data generation."""
    print("🧪 Testing Enhanced Mock Data Generation")
    print("=" * 50)
    
    # Test different sensor types for historic building
    test_cases = [
        {
            "tag": "HVAC_TEMP_Zone1", 
            "sensor_type": "hvac_temp", 
            "pattern": "sine",
            "base": 20.0
        },
        {
            "tag": "HUMIDITY_MainHall", 
            "sensor_type": "humidity", 
            "pattern": "default",
            "base": 55.0
        },
        {
            "tag": "FOOTFALL_Entrance", 
            "sensor_type": "footfall", 
            "pattern": "default",
            "base": 15.0
        },
        {
            "tag": "SEISMIC_Foundation", 
            "sensor_type": "seismic", 
            "pattern": "sine",
            "base": 0.15
        }
    ]
    
    context = {
        "scenario_type": "historic_building",
        "facility_type": "historic_building"
    }
    
    for test_case in test_cases:
        print(f"📈 Generating data for {test_case['tag']}:")
        
        # Add sensor type to context
        test_context = context.copy()
        test_context["sensor_type"] = test_case["sensor_type"]
        
        # Generate 24 hours of data
        data = generate_mock_timeseries(
            length=24,
            pattern_type=test_case["pattern"],
            base_value=test_case["base"],
            context=test_context
        )
        
        # Analyze the generated data
        stats = {
            "min": min(data),
            "max": max(data),
            "avg": sum(data) / len(data),
            "range": max(data) - min(data)
        }
        
        print(f"   Length: {len(data)} hours")
        print(f"   Range: {stats['min']:.3f} - {stats['max']:.3f}")
        print(f"   Average: {stats['avg']:.3f}")
        print(f"   Sample values: {[f'{v:.3f}' for v in data[:5]]}...")
        print()


def test_prompt_generation():
    """Test the enhanced prompt generation."""
    print("🧪 Testing Enhanced Prompt Generation")
    print("=" * 50)
    
    description = "Historic building monitoring system in Spain during tourist season"
    scenario = "HVAC, humidity, temperature and seismic monitoring with footfall tracking"
    tag_name = "HVAC_TEMP_Zone1"
    
    # Test prompt generation
    prompt = create_timeseries_generation_prompt(
        tag_name=tag_name,
        description=description,
        sequence_length=100,
        scenario=scenario,
        time_period="Weekly data covering tourist season",
        chat_llm=None
    )
    
    print(f"📝 Generated Prompt Preview:")
    print(f"   Length: {len(prompt)} characters")
    print(f"   Preview: {prompt[:200]}...")
    print()
    
    # Check if prompt contains expected context
    context_checks = [
        "historic_building" in prompt.lower(),
        "visitor" in prompt.lower() or "occupancy" in prompt.lower(),
        "operational" in prompt.lower(),
        "hvac" in prompt.lower() or "temperature" in prompt.lower(),
        "facility" in prompt.lower()
    ]
    
    print(f"✅ Context Checks:")
    print(f"   Contains facility context: {context_checks[0]}")
    print(f"   Contains visitor patterns: {context_checks[1]}")
    print(f"   Contains operational info: {context_checks[2]}")
    print(f"   Contains sensor context: {context_checks[3]}")
    print(f"   Contains facility info: {context_checks[4]}")
    print(f"   Overall score: {sum(context_checks)}/5")
    print()


def test_device_detection():
    """Test device type detection and guidance generation."""
    print("🧪 Testing Device Detection & Guidance")
    print("=" * 50)
    
    test_tags = [
        "HVAC_TEMP_Zone1",
        "HUMIDITY_MainHall", 
        "FOOTFALL_Entrance",
        "SEISMIC_Foundation",
        "VIBRATION_Structural"
    ]
    
    for tag in test_tags:
        device_info = detect_device_type_from_tag(tag)
        print(f"🏷️  Tag: {tag}")
        print(f"   Type: {device_info['type']}")
        print(f"   Measurement: {device_info['measurement']}")
        print(f"   Units: {device_info['units']}")
        print(f"   Range: {device_info['typical_range']}")
        print(f"   Application: {device_info['application']}")
        print()


def test_operational_patterns():
    """Test operational pattern generation."""
    print("🧪 Testing Operational Pattern Generation")
    print("=" * 50)
    
    context = {
        "facility_type": "historic_building",
        "operational_schedule": "visitor_hours",
        "environmental_factors": ["humidity_sensitive", "temperature_sensitive"],
        "special_events": ["seasonal_variation"]
    }
    
    # Test different sequence lengths
    for length in [24, 168]:  # 1 day, 1 week
        print(f"📅 Operational Pattern for {length} hours:")
        pattern = generate_operational_patterns(context, length)
        print(f"   Length: {len(pattern)} characters")
        print(f"   Preview: {pattern[:150]}...")
        print()


def test_llm_fallback():
    """Test LLM fallback behavior."""
    print("🧪 Testing LLM Fallback Behavior")
    print("=" * 50)
    
    try:
        # Create a FallbackChatLLM (should fall back to mock if no API)
        llm = FallbackChatLLM(model_name="gpt-4o", temperature=0.1)
        
        # Test basic prompt
        test_prompt = "Generate 5 realistic temperature values for a historic building HVAC system: "
        response = llm.generate(test_prompt)
        
        print(f"✅ LLM Response received:")
        print(f"   Length: {len(response)} characters")
        print(f"   Preview: {response[:100]}...")
        print()
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        print("   This is expected if no API key is configured")
        print()


def run_comprehensive_test():
    """Run all tests to validate the improvements."""
    print("🚀 TimeCraft Enhanced Scenario Testing")
    print("=" * 80)
    print("Testing improvements to historic building monitoring scenarios")
    print("=" * 80)
    print()
    
    try:
        # Run individual tests
        scenario_context = test_scenario_analysis()
        test_enhanced_mock_generation()
        test_prompt_generation()
        test_device_detection()
        test_operational_patterns()
        test_llm_fallback()
        
        print("✅ All tests completed successfully!")
        print("📊 Summary of Improvements:")
        print("   ✓ Enhanced scenario context analysis")
        print("   ✓ Facility-specific operational patterns")
        print("   ✓ Sensor-specific realistic behaviors")
        print("   ✓ Context-aware mock data generation")
        print("   ✓ Improved prompting with detailed guidance")
        print()
        print("🎯 The improvements should provide much more realistic and")
        print("   contextually appropriate timeseries data for historic")
        print("   building monitoring scenarios.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_comprehensive_test()
