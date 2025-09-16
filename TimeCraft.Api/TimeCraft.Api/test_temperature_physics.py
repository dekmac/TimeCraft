#!/usr/bin/env python3
"""
Test script to validate temperature physics in TimeCraft timeseries generation.
This script tests that temperature data follows realistic 24-hour thermal dynamics.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.timeseries_handlers import FallbackChatLLM, generate_timeseries_with_llm, validate_24_hour_temperature_pattern
from api.models import TimeHorizonInfo
import time

def test_24_hour_temperature_generation():
    """Test that 24-hour temperature generation follows physics"""
    print("🌡️  === TESTING 24-HOUR TEMPERATURE PHYSICS ===")
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
        print(f"📊 Total data points: {time_horizon.total_points}")
        
        # Test scenario
        scenario_description = "Outdoor temperature monitoring at a weather station for 24 hours. The sensor should show typical daily thermal patterns with cooler temperatures at night and warmer during the day."
        tag_name = "OUTDOOR_TEMPERATURE"
        tag_unit = "°C"
        
        print(f"\n🎯 Testing scenario: {scenario_description}")
        print(f"🏷️  Tag: {tag_name} ({tag_unit})")
        
        # Generate temperature data
        print(f"\n🔄 Generating 24-hour temperature data...")
        start_time = time.time()
        
        temperature_data = generate_timeseries_with_llm(
            tag_name=tag_name,
            description=scenario_description,
            sequence_length=24,
            tag_index=0,
            chat_llm=chat_llm,
            tag_unit=tag_unit,
            time_horizon=time_horizon
        )
        
        generation_time = time.time() - start_time
        print(f"✅ Generation completed in {generation_time:.2f} seconds")
        print(f"📊 Generated {len(temperature_data)} temperature values")
        
        # Display the temperature data with timestamps
        print(f"\n📈 24-HOUR TEMPERATURE PROFILE:")
        print("-" * 50)
        for i, temp in enumerate(temperature_data):
            hour = i
            time_str = f"{hour:02d}:00"
            print(f"   {time_str}  |  {temp:6.2f}°C")
        
        # Find min and max values and their times
        min_temp = min(temperature_data)
        max_temp = max(temperature_data) 
        min_hour = temperature_data.index(min_temp)
        max_hour = temperature_data.index(max_temp)
        daily_range = max_temp - min_temp
        
        print(f"\n📊 TEMPERATURE ANALYSIS:")
        print(f"   Minimum: {min_temp:.2f}°C at {min_hour:02d}:00")
        print(f"   Maximum: {max_temp:.2f}°C at {max_hour:02d}:00") 
        print(f"   Daily Range: {daily_range:.2f}°C")
        
        # Physics validation
        print(f"\n🔬 PHYSICS VALIDATION:")
        physics_issues = validate_24_hour_temperature_pattern(temperature_data, time_horizon)
        
        if not physics_issues:
            print("✅ PASSED: Temperature data follows realistic physics!")
            print("   ✓ Minimum occurs in early morning (3-6 AM)")
            print("   ✓ Maximum occurs in afternoon (1-4 PM)")
            print("   ✓ No unrealistic rapid changes")
            print("   ✓ Reasonable daily temperature range")
        else:
            print("❌ FAILED: Physics validation issues detected:")
            for issue in physics_issues:
                print(f"   • {issue}")
        
        # Additional physics checks
        print(f"\n🧪 DETAILED PHYSICS ANALYSIS:")
        
        # Check if minimum is in reasonable range (3-6 AM)
        min_time_ok = 3 <= min_hour <= 6
        print(f"   Minimum timing: {'✅ GOOD' if min_time_ok else '❌ BAD'} - {min_hour:02d}:00 ({'expected 03:00-06:00' if not min_time_ok else 'within expected range'})")
        
        # Check if maximum is in reasonable range (1-4 PM)  
        max_time_ok = 13 <= max_hour <= 16
        print(f"   Maximum timing: {'✅ GOOD' if max_time_ok else '❌ BAD'} - {max_hour:02d}:00 ({'expected 13:00-16:00' if not max_time_ok else 'within expected range'})")
        
        # Check daily range
        range_ok = 5.0 <= daily_range <= 20.0
        print(f"   Daily range: {'✅ GOOD' if range_ok else '❌ BAD'} - {daily_range:.1f}°C ({'expected 5-20°C' if not range_ok else 'realistic range'})")
        
        # Check for rapid changes
        rapid_changes = []
        for i in range(len(temperature_data) - 1):
            change = abs(temperature_data[i+1] - temperature_data[i])
            if change > 3.0:
                rapid_changes.append((i, i+1, change))
        
        print(f"   Rapid changes: {'✅ NONE' if not rapid_changes else f'❌ FOUND {len(rapid_changes)}'}")
        for i, j, change in rapid_changes:
            print(f"      • {change:.1f}°C change between {i:02d}:00 and {j:02d}:00")
        
        # Overall assessment
        all_good = min_time_ok and max_time_ok and range_ok and not rapid_changes and not physics_issues
        
        print(f"\n🏆 OVERALL PHYSICS ASSESSMENT:")
        if all_good:
            print("✅ EXCELLENT: Temperature data is physically realistic!")
            print("   This data would be suitable for real-world applications.")
        else:
            print("❌ ISSUES DETECTED: Temperature data has physics problems.")
            print("   The LLM needs better guidance to generate realistic thermal patterns.")
        
        return all_good, temperature_data, physics_issues
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False, [], [f"Test exception: {e}"]

def main():
    """Main test function"""
    print("🌡️  TimeCraft Temperature Physics Validation Test")
    print("=" * 60)
    
    success, data, issues = test_24_hour_temperature_generation()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 SUCCESS: Temperature generation follows physics!")
        print("   The enhanced validation and prompts are working correctly.")
    else:
        print("⚠️  IMPROVEMENTS NEEDED: Physics validation detected issues.")
        print("   The LLM prompts or validation logic may need refinement.")
    print("=" * 60)

if __name__ == "__main__":
    main()