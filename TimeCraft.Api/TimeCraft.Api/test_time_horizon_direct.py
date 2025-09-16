#!/usr/bin/env python3
"""
Direct test of time horizon functionality in generate_timeseries_with_llm function.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_time_horizon_directly():
    """Test time horizon functionality by calling the function directly."""
    
    print("🧪 Direct Time Horizon Test")
    print("=" * 50)
    
    try:
        # Import the function
        from api.timeseries_handlers import generate_timeseries_with_llm
        from api.models import TimeHorizonInfo
        
        # Mock LLM class for testing
        class MockLLM:
            def __init__(self):
                self.model_name = "mock-gpt-4o"
            
            def generate(self, prompt):
                print(f"📝 Mock LLM received prompt (first 200 chars):")
                print(f"    {prompt[:200]}...")
                
                # Check if time horizon context is in the prompt
                if "CRITICAL TIME HORIZON INSTRUCTIONS" in prompt:
                    print("✅ Time horizon context found in prompt!")
                elif "BASIC TIME CONTEXT" in prompt:
                    print("⚠️ Fallback time context found in prompt")
                else:
                    print("❌ No time context found in prompt!")
                
                # Return mock data
                return "23.5, 24.1, 23.8, 24.2, 23.9, 24.0, 23.7, 24.3, 23.6, 24.4"
        
        # Test scenarios
        scenarios = [
            {
                "name": "24 hours hourly", 
                "time_horizon": TimeHorizonInfo(
                    period=1,
                    unit="days",
                    granularity="hour", 
                    total_points=24
                ),
                "sequence_length": 24
            },
            {
                "name": "7 days hourly",
                "time_horizon": TimeHorizonInfo(
                    period=7,
                    unit="days",
                    granularity="hour",
                    total_points=168
                ),
                "sequence_length": 168
            },
            {
                "name": "No time horizon",
                "time_horizon": None,
                "sequence_length": 50
            }
        ]
        
        mock_llm = MockLLM()
        
        for scenario in scenarios:
            print(f"\n🔬 Testing: {scenario['name']}")
            
            try:
                result = generate_timeseries_with_llm(
                    tag_name="office_temperature",
                    description="Office building temperature monitoring",
                    sequence_length=scenario['sequence_length'],
                    tag_index=0,
                    chat_llm=mock_llm,
                    tag_unit="°C",
                    time_horizon=scenario['time_horizon']
                )
                
                print(f"   ✅ Generated {len(result)} data points")
                print(f"   📊 Data range: {min(result):.2f} to {max(result):.2f}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This might be due to module path issues or missing dependencies.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_time_horizon_directly()