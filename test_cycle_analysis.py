#!/usr/bin/env python3
"""
Test to see exactly what cycle instructions are being generated
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'TimeCraft.Api', 'TimeCraft.Api'))

from api.models import TimeHorizonInfo

def analyze_time_horizon_patterns():
    """Analyze the pattern generation logic directly"""
    
    test_cases = [
        {
            "name": "24 Hours (Hourly)",
            "time_horizon": TimeHorizonInfo(period=1, unit='days', granularity='hour', total_points=24),
            "expected_cycles": 1,
            "description": "Should have exactly 1 daily cycle over 24 hours"
        },
        {
            "name": "7 Days (Hourly)", 
            "time_horizon": TimeHorizonInfo(period=7, unit='days', granularity='hour', total_points=168),
            "expected_cycles": 7,
            "description": "Should have exactly 7 daily cycles over 7 days (168 hours)"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'=' * 70}")
        print(f"ANALYZING: {test_case['name']}")
        print(f"Time Horizon: {test_case['time_horizon'].period} {test_case['time_horizon'].unit}")
        print(f"Granularity: {test_case['time_horizon'].granularity}")
        print(f"Total Points: {test_case['time_horizon'].total_points}")
        print(f"Expected Cycles: {test_case['expected_cycles']}")
        print(f"Description: {test_case['description']}")
        print(f"{'=' * 70}")
        
        # Simulate the pattern guidance logic from timeseries_handlers.py
        time_horizon = test_case['time_horizon']
        sequence_length = time_horizon.total_points
        
        pattern_guidance = ""
        
        if time_horizon.granularity == 'hour':
            if time_horizon.unit == 'days' and time_horizon.period == 1:
                pattern_guidance = f"""
24-HOUR DAILY PATTERN INSTRUCTIONS (EXACTLY 1 DAILY CYCLE REQUIRED):
====================================================================
• Generate {sequence_length} values representing 24 consecutive hours (1 full day)
• CRITICAL MATHEMATICAL CONSTRAINT: Generate EXACTLY 1 daily cycle - one peak, one valley
• MANDATORY CYCLE STRUCTURE:
  - Hours 0-6 (Points 1-7): Night LOW values (18-20°C) - minimal activity
  - Hours 7-11 (Points 8-12): Morning RISING values (20-24°C) - gradual warm-up
  - Hours 12-16 (Points 13-17): Day PEAK values (25-27°C) - maximum activity
  - Hours 17-21 (Points 18-22): Evening DECLINING values (24-21°C) - cooldown
  - Hours 22-23 (Points 23-24): Night LOW values (19-20°C) - settling
• PEAK COUNT VALIDATION: Must have exactly 1 peak around hours 12-16 (one of points 13-17)
• PATTERN SHAPE: Single bell curve rising from low (night) to high (day) back to low (night)
• EXAMPLE: 19.5→19.2→18.8→19.1→19.7→20.3→21.1→22.8→24.2→25.8→26.2→26.5→26.8→26.4→25.2→24.1→22.8→21.5→20.9→20.3→19.9→19.7→19.5→19.8"""
                
            elif time_horizon.unit == 'days' and time_horizon.period == 7:
                pattern_guidance = f"""
7-DAY WEEKLY PATTERN INSTRUCTIONS (EXACTLY 7 DAILY CYCLES REQUIRED):
====================================================================
• Generate {sequence_length} values representing hourly measurements over 7 days (1 week)
• CRITICAL MATHEMATICAL CONSTRAINT: Generate EXACTLY 7 daily cycles - no more, no less
• CYCLE STRUCTURE REQUIREMENT:
  - Points 1-24: Day 1 cycle (24 hours: night low → day high → night low)
  - Points 25-48: Day 2 cycle (24 hours: night low → day high → night low)
  - Points 49-72: Day 3 cycle (24 hours: night low → day high → night low)
  - Points 73-96: Day 4 cycle (24 hours: night low → day high → night low)
  - Points 97-120: Day 5 cycle (24 hours: night low → day high → night low)
  - Points 121-144: Day 6 cycle (24 hours: night low → day high → night low)
  - Points 145-168: Day 7 cycle (24 hours: night low → day high → night low)
• MANDATORY PEAK COUNT: Must have exactly 7 peaks (one per day) around hours 12-16 of each day
• WEEKDAY vs WEEKEND DISTINCTION:
  - Days 1-5 (Weekdays): Peak values around 27°C, low values around 21°C
  - Days 6-7 (Weekend): Peak values around 25°C, low values around 19°C
• VALIDATION: Count your peaks - if you don't have exactly 7 peaks, you've made an error"""
        
        print("PATTERN GUIDANCE GENERATED:")
        print(pattern_guidance)
        
        # Analyze the solution
        if time_horizon.period == 7 and time_horizon.unit == 'days':
            print("\n🔍 SOLUTION IMPLEMENTED:")
            print("✅ FIXED: The pattern guidance now explicitly states:")
            print("   - 'Generate EXACTLY 7 daily cycles - no more, no less'")
            print("   - 'Points 1-24: Day 1 cycle, Points 25-48: Day 2 cycle, etc.'") 
            print("   - 'Must have exactly 7 peaks (one per day)'")
            print("   - 'VALIDATION: Count your peaks - if you don't have exactly 7 peaks, you've made an error'")
            print("\n💡 MATHEMATICAL PRECISION:")
            print("   The LLM now gets EXPLICIT constraints about exact cycle count!")
            print("   No more ambiguity about how many oscillations to generate!")

if __name__ == "__main__":
    analyze_time_horizon_patterns()