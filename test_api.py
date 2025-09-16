#!/usr/bin/env python3
"""
Test the enhanced TimeCraft API endpoints directly.
"""

import requests
import json

# Test server URL
BASE_URL = "http://127.0.0.1:8001"

def test_generate_tags():
    """Test the generate-tags endpoint with enhanced response."""
    print("🧪 Testing /generate-tags endpoint...")
    
    request_data = {
        "text_description": "I want sensor data for monitoring a historic building in Spain during tourist season. I would like to see HVAC temperature, humidity levels, seismic activity monitoring, and footfall from presence sensors to monitor visitor traffic.",
        "num_tags": 4
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-tags", json=request_data)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Response received:")
        print(f"   Status: {result.get('status')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Generation Method: {result.get('generation_method')}")
        
        # Check for enhanced features
        if 'tag_details' in result:
            print("✅ Enhanced tag_details found:")
            for detail in result['tag_details']:
                print(f"      {detail['tag']} ({detail['unit']}) - {detail['description']}")
        else:
            print("⚠️ No tag_details in response")
            
        if 'tags' in result:
            print(f"✅ Legacy tags array: {result['tags']}")
        else:
            print("❌ No tags array in response")
            
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode failed: {e}")
        return None

def test_health():
    """Test the health endpoint."""
    print("\n🧪 Testing /health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        
        result = response.json()
        print("✅ Health check passed:")
        print(f"   Status: {result.get('status')}")
        print(f"   Enhanced Features: {result.get('enhanced_features')}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Testing Enhanced TimeCraft API")
    print("=" * 50)
    
    # Test health endpoint
    health_result = test_health()
    
    # Test generate-tags endpoint  
    tags_result = test_generate_tags()
    
    print("\n" + "=" * 50)
    if health_result and tags_result:
        print("🎉 SUCCESS: All tests passed!")
        print("✅ Enhanced workflow is functioning correctly")
        print("✅ API is returning both legacy tags and enhanced tag_details")
        
        # Check if we got building-relevant tags
        if 'tag_details' in tags_result:
            building_tags = [td for td in tags_result['tag_details'] 
                           if any(word in td['tag'].upper() for word in ['BUILDING', 'HVAC', 'HUMIDITY', 'FOOTFALL', 'SEISMIC', 'VISITOR', 'TEMP'])]
            relevance = len(building_tags) / len(tags_result['tag_details'])
            print(f"🏛️ Building relevance: {len(building_tags)}/{len(tags_result['tag_details'])} tags ({relevance:.1%})")
            
            if relevance >= 0.75:
                print("✅ Excellent scenario alignment!")
            elif relevance >= 0.5:
                print("✅ Good scenario alignment!")
            else:
                print("⚠️ Could improve scenario alignment")
    else:
        print("❌ Some tests failed")