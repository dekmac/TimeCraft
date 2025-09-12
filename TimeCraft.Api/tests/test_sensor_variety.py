#!/usr/bin/env python3
"""
Test different structural monitoring sensor types
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.timeseries_handlers import FallbackChatLLM

def test_sensor_type(sensor_type, prompt):
    """Test a specific sensor type with its prompt."""
    print(f"\n🔬 Testing {sensor_type}:")
    print(f"📝 Prompt: {prompt}")
    
    chat_llm = FallbackChatLLM(model_name="gpt-4o")
    response = chat_llm.generate(prompt)
    
    # Parse values
    if "," in response:
        try:
            values = [float(x.strip()) for x in response.split(",") if x.strip()]
            print(f"✅ Generated {len(values)} values")
            print(f"📊 Range: {min(values):.3f} to {max(values):.3f}")
            print(f"🎯 Sample: {values[:6]} (first 6)")
            
            # Check for variation
            avg = sum(values) / len(values)
            std_dev = (sum((x - avg) ** 2 for x in values) / len(values)) ** 0.5
            print(f"📈 Avg: {avg:.3f}, StdDev: {std_dev:.3f}")
            
        except ValueError as e:
            print(f"❌ Error parsing: {e}")
    else:
        print(f"❌ No comma-separated values found")

if __name__ == "__main__":
    # Test different sensor types
    
    test_sensor_type("Vibration Sensor", 
        "Generate vibration data for bridge monitoring over 12 hours")
    
    test_sensor_type("Strain Gauge", 
        "Generate strain gauge readings for structural beam monitoring")
    
    test_sensor_type("Displacement Sensor", 
        "Generate displacement measurements for foundation settlement monitoring")
    
    test_sensor_type("Temperature Sensor", 
        "Generate temperature data for structural thermal monitoring")
    
    test_sensor_type("Tilt Sensor", 
        "Generate tilt measurements for building inclination monitoring")
    
    test_sensor_type("Generic Structural", 
        "Generate structural health monitoring data for analysis")
