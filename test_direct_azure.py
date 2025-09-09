#!/usr/bin/env python3
"""
Direct test of Azure OpenAI credentials and endpoint.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check the exact values
print("=== Direct Environment Values ===")
api_base = os.environ.get("OPENAI_API_BASE")
api_key = os.environ.get("OPENAI_API_KEY")
api_version = os.environ.get("OPENAI_API_VERSION")
deployment = os.environ.get("OPENAI_DEPLOYMENT_NAME")

print(f"API Base: {api_base}")
print(f"API Key: {api_key[:10]}...{api_key[-10:] if api_key and len(api_key) > 20 else 'SHORT/MISSING'}")
print(f"API Version: {api_version}")
print(f"Deployment: {deployment}")

# Test with exact configuration
if api_base and api_key and api_version and deployment:
    try:
        from openai import AzureOpenAI
        
        # Test the exact endpoint format
        print(f"\n=== Testing Endpoint ===")
        print(f"Full endpoint: {api_base}")
        
        # Ensure endpoint ends with /
        if not api_base.endswith('/'):
            api_base_fixed = api_base + '/'
            print(f"Fixed endpoint: {api_base_fixed}")
        else:
            api_base_fixed = api_base
        
        client = AzureOpenAI(
            azure_endpoint=api_base_fixed,
            api_key=api_key,
            api_version=api_version
        )
        
        print(f"\n=== Making Test Call ===")
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "user", "content": "Say hello"}
            ],
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        print(f"✅ SUCCESS! Response: {result}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        
        # Try with different endpoint format
        if "/openai/" not in api_base:
            try:
                print(f"\n=== Trying with /openai/ path ===")
                alt_endpoint = api_base.rstrip('/') + '/openai/'
                print(f"Alternative endpoint: {alt_endpoint}")
                
                client2 = AzureOpenAI(
                    azure_endpoint=alt_endpoint,
                    api_key=api_key,
                    api_version=api_version
                )
                
                response2 = client2.chat.completions.create(
                    model=deployment,
                    messages=[
                        {"role": "user", "content": "Say hello"}
                    ],
                    temperature=0.3
                )
                
                result2 = response2.choices[0].message.content
                print(f"✅ SUCCESS with /openai/! Response: {result2}")
                
            except Exception as e2:
                print(f"❌ Also failed with /openai/: {e2}")
else:
    print("❌ Missing required environment variables")
