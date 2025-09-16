#!/usr/bin/env python3
"""
Simple test to call the API and see GPT-5-mini response
"""
import requests
import json

def test_api_call():
    """Make a simple API call to test GPT-5-mini response."""
    
    url = "http://localhost:8000/generate-timeseries-llm"
    
    # Simple test payload
    payload = {
        "tag_name": "TEST_TEMP_01",
        "tag_unit": "°C", 
        "sequence_length": 10,
        "description": "Test temperature sensor",
        "tag_index": 0,
        "time_horizon": {
            "period": 1,
            "unit": "hours", 
            "granularity": "minute"
        }
    }
    
    print("🧪 Testing GPT-5-mini API call...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("="*80)
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response:")
            print(json.dumps(result, indent=2))
            
            values = result.get('values', [])
            print(f"\n📊 Values received: {len(values)} items")
            if values:
                print(f"First few: {values[:10]}")
                print(f"All values: {values}")
            else:
                print("❌ NO VALUES RETURNED!")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_call()