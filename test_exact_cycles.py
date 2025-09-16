#!/usr/bin/env python3
"""
Test to verify that time horizon instructions produce the correct number of cycles
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'TimeCraft.Api', 'TimeCraft.Api'))

from api.timeseries_handlers import generate_timeseries_with_llm
from api.models import TimeHorizonInfo
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MockLLMAgent:
    """Mock LLM that returns the prompt for inspection"""
    
    async def generate_timeseries(self, prompt, num_points, metadata=None):
        print("=" * 80)
        print("PROMPT SENT TO LLM:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        print(f"Expected number of points: {num_points}")
        
        # Analyze the prompt for cycle information
        if "7-DAY WEEKLY PATTERN" in prompt:
            print("\n🔍 ANALYSIS FOR 7-DAY PATTERN:")
            print("- Should have exactly 7 daily cycles (7 peaks and 7 valleys)")
            print("- Each cycle should be 24 hours (24 data points if hourly)")
            print("- Total points should be 7 × 24 = 168 points")
            
        if "24-HOUR DAILY PATTERN" in prompt:
            print("\n🔍 ANALYSIS FOR 24-HOUR PATTERN:")
            print("- Should have exactly 1 daily cycle (1 peak and 1 valley)")
            print("- Total points should be 24 points")
            
        return [20.0] * num_points  # Return dummy data

async def test_time_horizons():
    """Test different time horizons to see their cycle instructions"""
    
    mock_agent = MockLLMAgent()
    
    test_cases = [
        {
            "name": "24 Hours (Hourly)",
            "time_horizon": TimeHorizonInfo(period=1, unit='days', granularity='hour', total_points=24),
            "expected_points": 24,
            "expected_cycles": 1
        },
        {
            "name": "7 Days (Hourly)", 
            "time_horizon": TimeHorizonInfo(period=7, unit='days', granularity='hour', total_points=168),
            "expected_points": 168,  # 7 × 24
            "expected_cycles": 7
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'=' * 60}")
        print(f"TESTING: {test_case['name']}")
        print(f"Expected Points: {test_case['expected_points']}")
        print(f"Expected Daily Cycles: {test_case['expected_cycles']}")
        print(f"{'=' * 60}")
        
        try:
            result = await generate_timeseries_with_llm(
                agent=mock_agent,
                prompt="Generate humidity data for a server room",
                time_horizon=test_case['time_horizon'],
                metric_name="Humidity",
                metadata={"location": "Server Room"}
            )
            
            print(f"✅ Generated {len(result)} data points")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_time_horizons())