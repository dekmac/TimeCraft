#!/usr/bin/env python3
"""
Test script to validate multi-sensor physics in TimeCraft timeseries generation.
This script tests temperature, humidity, and pressure sensors with realistic physics.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.timeseries_handlers import (FallbackChatLLM, generate_timeseries_with_llm, 
                                    validate_24_hour_temperature_pattern, 
                                    validate_humidity_pattern, validate_pressure_pattern)
from api.models import TimeHorizonInfo
import time

def test_environmental_sensor(sensor_name, sensor_unit, scenario, expected_physics):
    """Test a specific environmental sensor type"""
    print(f"\n🌡️  === TESTING {sensor_name.upper()} SENSOR ===")
    print("=" * 60)
    
    try:
        # Create LLM instance
        print("🚀 Creating FallbackChatLLM...")
        chat_llm = FallbackChatLLM(model_name='gpt-4o', temperature=0.1)
        print("✅ LLM created successfully")
        
        # Create 24-hour time horizon (hourly measurements)
        time_horizon = TimeHorizonInfo(
            period=1,
            unit='days', 
            granularity='hour',
            total_points=24
        )
        
        print(f"📅 Time horizon: {time_horizon.period} {time_horizon.unit} with {time_horizon.granularity} granularity")
        print(f"🎯 Testing scenario: {scenario}")
        print(f"🏷️  Tag: {sensor_name} ({sensor_unit})")
        
        # Generate sensor data
        print(f"\n🔄 Generating 24-hour {sensor_name.lower()} data...")
        start_time = time.time()
        
        sensor_data = generate_timeseries_with_llm(
            tag_name=sensor_name,
            description=scenario,
            sequence_length=24,
            tag_index=0,
            chat_llm=chat_llm,
            tag_unit=sensor_unit,
            time_horizon=time_horizon
        )
        
        generation_time = time.time() - start_time
        print(f"✅ Generation completed in {generation_time:.2f} seconds")
        print(f"📊 Generated {len(sensor_data)} {sensor_name.lower()} values")
        
        # Display the sensor data with timestamps
        print(f"\n📈 24-HOUR {sensor_name.upper()} PROFILE:")
        print("-" * 50)
        for i, value in enumerate(sensor_data):
            hour = i
            time_str = f"{hour:02d}:00"
            print(f"   {time_str}  |  {value:6.2f}{sensor_unit}")
        
        # Find min and max values and their times
        min_value = min(sensor_data)
        max_value = max(sensor_data) 
        min_hour = sensor_data.index(min_value)
        max_hour = sensor_data.index(max_value)
        daily_range = max_value - min_value
        
        print(f"\n📊 {sensor_name.upper()} ANALYSIS:")
        print(f"   Minimum: {min_value:.2f}{sensor_unit} at {min_hour:02d}:00")
        print(f"   Maximum: {max_value:.2f}{sensor_unit} at {max_hour:02d}:00") 
        print(f"   Daily Range: {daily_range:.2f}{sensor_unit}")
        
        # Sensor-specific physics validation
        print(f"\n🔬 PHYSICS VALIDATION:")
        physics_issues = []
        
        if 'temp' in sensor_name.lower():
            physics_issues = validate_24_hour_temperature_pattern(sensor_data, time_horizon)
        elif 'humidity' in sensor_name.lower():
            physics_issues = validate_humidity_pattern(sensor_data, time_horizon, sensor_name)
        elif 'pressure' in sensor_name.lower():
            physics_issues = validate_pressure_pattern(sensor_data, time_horizon, sensor_name)
        
        if not physics_issues:
            print(f"✅ PASSED: {sensor_name} data follows realistic physics!")
            for expectation in expected_physics:
                print(f"   ✓ {expectation}")
        else:
            print(f"❌ FAILED: Physics validation issues detected:")
            for issue in physics_issues:
                print(f"   • {issue}")
        
        # Additional physics checks based on sensor type
        print(f"\n🧪 DETAILED PHYSICS ANALYSIS:")
        
        if 'temp' in sensor_name.lower():
            # Temperature-specific checks
            min_time_ok = 3 <= min_hour <= 6
            max_time_ok = 13 <= max_hour <= 16
            range_ok = 5.0 <= daily_range <= 20.0
            
            print(f"   Minimum timing: {'✅ GOOD' if min_time_ok else '❌ BAD'} - {min_hour:02d}:00 ({'expected 03:00-06:00' if not min_time_ok else 'within expected range'})")
            print(f"   Maximum timing: {'✅ GOOD' if max_time_ok else '❌ BAD'} - {max_hour:02d}:00 ({'expected 13:00-16:00' if not max_time_ok else 'within expected range'})")
            print(f"   Daily range: {'✅ GOOD' if range_ok else '❌ BAD'} - {daily_range:.1f}°C ({'expected 5-20°C' if not range_ok else 'realistic range'})")
            
            physics_ok = min_time_ok and max_time_ok and range_ok and not physics_issues
            
        elif 'humidity' in sensor_name.lower():
            # Humidity-specific checks
            values_in_range = all(0 <= v <= 100 for v in sensor_data)
            max_time_ok = 3 <= max_hour <= 7  # Humidity peaks in early morning
            min_time_ok = 13 <= min_hour <= 17  # Humidity minimum in afternoon
            range_ok = 15.0 <= daily_range <= 50.0
            
            print(f"   Value range: {'✅ GOOD' if values_in_range else '❌ BAD'} - all values 0-100%")
            print(f"   Maximum timing: {'✅ GOOD' if max_time_ok else '❌ BAD'} - {max_hour:02d}:00 ({'expected 03:00-07:00' if not max_time_ok else 'within expected range'})")
            print(f"   Minimum timing: {'✅ GOOD' if min_time_ok else '❌ BAD'} - {min_hour:02d}:00 ({'expected 13:00-17:00' if not min_time_ok else 'within expected range'})")
            print(f"   Daily range: {'✅ GOOD' if range_ok else '❌ BAD'} - {daily_range:.1f}% ({'expected 15-50%' if not range_ok else 'realistic range'})")
            
            physics_ok = values_in_range and max_time_ok and min_time_ok and range_ok and not physics_issues
            
        elif 'pressure' in sensor_name.lower():
            # Pressure-specific checks
            is_atmospheric = any(900 <= v <= 1100 for v in sensor_data)
            if is_atmospheric:
                range_ok = daily_range <= 20.0  # Atmospheric pressure shouldn't vary too much daily
                values_ok = all(800 <= v <= 1200 for v in sensor_data)
            else:
                range_ok = True  # System pressure has different constraints
                values_ok = True
            
            print(f"   Pressure type: {'Atmospheric' if is_atmospheric else 'System'}")
            print(f"   Value range: {'✅ GOOD' if values_ok else '❌ BAD'}")
            print(f"   Daily variation: {'✅ GOOD' if range_ok else '❌ BAD'} - {daily_range:.1f} units")
            
            physics_ok = values_ok and range_ok and not physics_issues
        
        else:
            physics_ok = not physics_issues
        
        # Check for rapid changes
        rapid_changes = []
        for i in range(len(sensor_data) - 1):
            change = abs(sensor_data[i+1] - sensor_data[i])
            if 'temp' in sensor_name.lower() and change > 3.0:
                rapid_changes.append((i, i+1, change))
            elif 'humidity' in sensor_name.lower() and change > 15.0:
                rapid_changes.append((i, i+1, change))
            elif 'pressure' in sensor_name.lower() and change > 10.0:
                rapid_changes.append((i, i+1, change))
        
        print(f"   Rapid changes: {'✅ NONE' if not rapid_changes else f'❌ FOUND {len(rapid_changes)}'}")
        for i, j, change in rapid_changes:
            print(f"      • {change:.1f}{sensor_unit} change between {i:02d}:00 and {j:02d}:00")
        
        # Overall assessment
        physics_ok = physics_ok and not rapid_changes
        
        print(f"\n🏆 OVERALL PHYSICS ASSESSMENT:")
        if physics_ok:
            print(f"✅ EXCELLENT: {sensor_name} data is physically realistic!")
            print("   This data would be suitable for real-world applications.")
        else:
            print(f"❌ ISSUES DETECTED: {sensor_name} data has physics problems.")
            print("   The LLM needs better guidance to generate realistic patterns.")
        
        return physics_ok, sensor_data, physics_issues
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False, [], [f"Test exception: {e}"]

def main():
    """Main test function for multiple environmental sensors"""
    print("🌡️  TimeCraft Multi-Sensor Physics Validation Test")
    print("=" * 60)
    
    # Test scenarios for different sensor types
    test_scenarios = [
        {
            "sensor_name": "OUTDOOR_TEMPERATURE",
            "sensor_unit": "°C",
            "scenario": "Outdoor temperature monitoring at a weather station for 24 hours. The sensor should show typical daily thermal patterns with cooler temperatures at night and warmer during the day.",
            "expected_physics": [
                "Minimum occurs in early morning (3-6 AM)",
                "Maximum occurs in afternoon (1-4 PM)",
                "No unrealistic rapid changes",
                "Reasonable daily temperature range"
            ]
        },
        {
            "sensor_name": "OUTDOOR_HUMIDITY", 
            "sensor_unit": "%",
            "scenario": "Outdoor humidity monitoring at a weather station for 24 hours. The sensor should show typical daily humidity patterns with higher humidity at night and lower during the day.",
            "expected_physics": [
                "Maximum occurs in early morning (3-7 AM)", 
                "Minimum occurs in afternoon (1-5 PM)",
                "Values stay within 0-100% range",
                "Inverse relationship to temperature"
            ]
        },
        {
            "sensor_name": "ATMOSPHERIC_PRESSURE",
            "sensor_unit": "hPa", 
            "scenario": "Atmospheric pressure monitoring at a weather station for 24 hours. The sensor should show gradual pressure changes following weather patterns.",
            "expected_physics": [
                "Gradual changes only (no sudden spikes)",
                "Values within atmospheric range (990-1020 hPa)",
                "Smooth pressure variations",
                "Realistic daily pressure drift"
            ]
        }
    ]
    
    results = []
    
    # Test each sensor type
    for test_case in test_scenarios:
        success, data, issues = test_environmental_sensor(
            test_case["sensor_name"],
            test_case["sensor_unit"], 
            test_case["scenario"],
            test_case["expected_physics"]
        )
        results.append((test_case["sensor_name"], success))
    
    # Overall summary
    print(f"\n{'='*60}")
    print("🏆 MULTI-SENSOR PHYSICS TEST SUMMARY:")
    
    all_passed = True
    for sensor_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED" 
        print(f"   {sensor_name}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 SUCCESS: All environmental sensors follow physics!")
        print("   The enhanced validation system works for multiple sensor types.")
    else:
        print("\n⚠️  SOME ISSUES: Not all sensors passed physics validation.")
        print("   Consider refining prompts for failed sensor types.")
    print("=" * 60)

if __name__ == "__main__":
    main()