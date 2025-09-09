#!/usr/bin/env python3

import os
from openai import AzureOpenAI

def test_azure_openai():
    print("=== Azure OpenAI Test ===")
    
    # Check environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    api_base = os.environ.get('OPENAI_API_BASE')
    api_version = os.environ.get('OPENAI_API_VERSION')
    deployment = os.environ.get('OPENAI_DEPLOYMENT_NAME')
    
    print(f"API Key: {'SET' if api_key else 'NOT SET'} (length: {len(api_key) if api_key else 0})")
    print(f"API Base: {api_base}")
    print(f"API Version: {api_version}")
    print(f"Deployment: {deployment}")
    
    if not all([api_key, api_base, api_version, deployment]):
        print("❌ Missing required environment variables")
        return False
    
    try:
        # Create Azure OpenAI client
        client = AzureOpenAI(
            azure_endpoint=api_base,
            api_key=api_key,
            api_version=api_version
        )
        
        print(f"\n🚀 Testing Azure OpenAI with deployment: {deployment}")
        
        # Simple test call
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "user", "content": "Say 'Hello from Azure OpenAI!'"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ Success! Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_azure_openai()
