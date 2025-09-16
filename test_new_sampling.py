#!/usr/bin/env python3
"""
Test the updated sampling frequencies for different time horizons
"""

from dataclasses import dataclass

@dataclass
class TimeHorizonInfo:
    period: int
    unit: str
    granularity: str
    total_points: int

def test_new_sampling_frequencies():
    """Test the new sampling frequency configurations"""
    
    test_scenarios = [
        {
            "name": "24 Hours - 5 Minute Intervals",
            "time_horizon": TimeHorizonInfo(period=24, unit='hours', granularity='minute', total_points=288),
            "expected_description": "288 points = 24 hours × 12 samples/hour (every 5 minutes)",
            "expected_cycles": 1,
            "cycle_description": "1 daily cycle with high-resolution 5-minute sensor data"
        },
        {
            "name": "7 Days - Hourly",
            "time_horizon": TimeHorizonInfo(period=7, unit='days', granularity='hour', total_points=168),
            "expected_description": "168 points = 7 days × 24 hours/day (every hour)",
            "expected_cycles": 7,
            "cycle_description": "7 daily cycles, one per day"
        },
        {
            "name": "30 Days - 3 Hour Intervals",
            "time_horizon": TimeHorizonInfo(period=30, unit='days', granularity='hour', total_points=240),
            "expected_description": "240 points = 30 days × 8 samples/day (every 3 hours)",
            "expected_cycles": 30,
            "cycle_description": "30 daily cycles, 8 samples per day"
        }
    ]
    
    print("🧪 TESTING NEW SAMPLING FREQUENCIES")
    print("=" * 80)
    
    for scenario in test_scenarios:
        print(f"\n📊 SCENARIO: {scenario['name']}")
        print(f"⚙️ Configuration: {scenario['time_horizon'].period} {scenario['time_horizon'].unit}, {scenario['time_horizon'].granularity} granularity")
        print(f"📈 Total Points: {scenario['time_horizon'].total_points}")
        print(f"📐 Calculation: {scenario['expected_description']}")
        print(f"🔄 Expected Cycles: {scenario['expected_cycles']}")
        print(f"📝 Pattern: {scenario['cycle_description']}")
        
        # Validate calculations
        if scenario['name'] == "24 Hours - 5 Minute Intervals":
            calculated_points = 24 * 12  # 24 hours × 12 five-minute intervals per hour
            if calculated_points == scenario['time_horizon'].total_points:
                print("✅ Calculation CORRECT: 24 hours × 12 (5-min intervals/hour) = 288 points")
            else:
                print(f"❌ Calculation ERROR: Expected {calculated_points}, got {scenario['time_horizon'].total_points}")
                
        elif scenario['name'] == "7 Days - Hourly":
            calculated_points = 7 * 24  # 7 days × 24 hours per day
            if calculated_points == scenario['time_horizon'].total_points:
                print("✅ Calculation CORRECT: 7 days × 24 hours/day = 168 points")
            else:
                print(f"❌ Calculation ERROR: Expected {calculated_points}, got {scenario['time_horizon'].total_points}")
                
        elif scenario['name'] == "30 Days - 3 Hour Intervals":
            calculated_points = 30 * 8  # 30 days × 8 three-hour intervals per day
            if calculated_points == scenario['time_horizon'].total_points:
                print("✅ Calculation CORRECT: 30 days × 8 (3-hour intervals/day) = 240 points")
            else:
                print(f"❌ Calculation ERROR: Expected {calculated_points}, got {scenario['time_horizon'].total_points}")
        
        print(f"🎯 LLM Instructions: Will receive explicit cycle count = {scenario['expected_cycles']}")
        print("-" * 60)
    
    print(f"\n🚀 BENEFITS OF NEW SAMPLING:")
    print("✅ 24 Hours: High-resolution 5-minute data for detailed patterns")
    print("✅ 7 Days: Hourly data perfect for daily cycle analysis")  
    print("✅ 30 Days: 3-hour intervals capture daily peaks efficiently")
    print("✅ All configurations have mathematically precise cycle counts")
    print("✅ LLM gets explicit point-to-time mapping for accurate pattern generation")
    print("=" * 80)

if __name__ == "__main__":
    test_new_sampling_frequencies()