#!/usr/bin/env python3
"""
Test GPT-5-mini with the fixed prompt system
"""

import requests

def test_gpt5mini_timeseries():
    """Test the GPT-5-mini optimized prompts"""
    
    # Test data
    url = "http://localhost:8000/generate-timeseries-for-tag"
    
    test_data = {
        "tag_name": "SAGR_NAVE_TEMP_01",
        "text_description": "Generate temperature data for historic building monitoring",
        "sequence_length": 12,  # Small number for quick test
        "time_horizon": {
            "period": 2,
            "unit": "hours", 
            "granularity": "10 minutes",
            "total_points": 12
        }
    }
    
    print("🧪 Testing GPT-5-mini optimized timeseries generation...")
    print(f"🏷️ Tag: {test_data['tag_name']}")
    print(f"📊 Requesting {test_data['sequence_length']} data points")
    
    try:
        response = requests.post(url, json=test_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Response successful!")
            print(f"📈 Generated {len(result.get('values', []))} data points")
            print(f"🔧 Method: {result.get('method', 'unknown')}")
            
            if result.get('values'):
                values = result['values'][:10]  # Show first 10
                print(f"📝 Sample values: {values}")
                
                # Check for the zero-values bug
                if all(v == 0 for v in result['values']):
                    print("❌ BUG: All values are zero!")
                else:
                    print("✅ Values look non-zero and realistic")
            else:
                print("❌ BUG: No values returned!")
                
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure the API server is running on localhost:8000")

if __name__ == "__main__":
    test_gpt5mini_timeseries()