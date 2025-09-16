#!/usr/bin/env python3
"""
Test script to verify time horizon context is working in the LLM generation.
"""

import requests
import json

def test_time_horizon_context():
    """Test that different time horizons produce different data patterns."""
    
    base_url = "http://localhost:8080"  # Adjust if your API runs on different port
    
    # Test data
    test_scenarios = [
        {
            "name": "24 hours hourly",
            "request": {
                "tag_name": "office_temperature",
                "text_description": "Office building temperature monitoring",
                "sequence_length": 24,
                "time_horizon": {
                    "period": 1,
                    "unit": "days",
                    "granularity": "hour",
                    "total_points": 24
                }
            }
        },
        {
            "name": "7 days hourly", 
            "request": {
                "tag_name": "office_temperature",
                "text_description": "Office building temperature monitoring",
                "sequence_length": 168,
                "time_horizon": {
                    "period": 7,
                    "unit": "days", 
                    "granularity": "hour",
                    "total_points": 168
                }
            }
        },
        {
            "name": "4 hours minutely",
            "request": {
                "tag_name": "office_temperature",
                "text_description": "Office building temperature monitoring", 
                "sequence_length": 240,
                "time_horizon": {
                    "period": 4,
                    "unit": "hours",
                    "granularity": "minute", 
                    "total_points": 240
                }
            }
        }
    ]
    
    print("🧪 Testing Time Horizon Context in LLM Generation")
    print("=" * 60)
    
    for scenario in test_scenarios:
        print(f"\n🔬 Testing: {scenario['name']}")
        print(f"   Time Horizon: {scenario['request']['time_horizon']['period']} {scenario['request']['time_horizon']['unit']} with {scenario['request']['time_horizon']['granularity']} granularity")
        
        try:
            response = requests.post(
                f"{base_url}/generate-timeseries-for-tag",
                json=scenario['request'],
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'success':
                    timeseries = result.get('timeseries', [])
                    timestamps = result.get('timestamps', [])
                    method = result.get('generation_method', 'unknown')
                    
                    print(f"   ✅ Success - Generated {len(timeseries)} points using {method}")
                    print(f"   📊 Data range: {min(timeseries):.2f} to {max(timeseries):.2f}")
                    if timestamps:
                        print(f"   🕒 Time range: {timestamps[0]} to {timestamps[-1]}")
                    else:
                        print(f"   ⚠️ No timestamps returned")
                        
                    # Show first few data points
                    preview = timeseries[:5] if len(timeseries) > 5 else timeseries
                    print(f"   📈 Preview: {[round(x, 2) for x in preview]}...")
                else:
                    print(f"   ❌ Failed: {result.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed. Check the logs above to see if time horizon context is working.")
    print("💡 If all scenarios return similar patterns, the time horizon context may not be working.")

if __name__ == "__main__":
    test_time_horizon_context()