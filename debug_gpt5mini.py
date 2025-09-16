#!/usr/bin/env python3
"""
Debug GPT-5-mini empty response issue with step-by-step testing
"""

import os
import sys
sys.path.append('TimeCraft.Api/TimeCraft.Api')

try:
    from api.timeseries_handlers import FallbackChatLLM, get_gpt5mini_optimized_prompt
    print("✅ Successfully imported TimeCraft modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔄 Trying alternative import...")
    sys.path.append('.')
    sys.path.append('TimeCraft.Api')
    try:
        from TimeCraft.Api.api.timeseries_handlers import FallbackChatLLM, get_gpt5mini_optimized_prompt
        print("✅ Successfully imported with alternative path")
    except ImportError as e2:
        print(f"❌ Alternative import failed: {e2}")
        print("💡 Run this from the TimeCraft root directory")
        sys.exit(1)

def test_gpt5mini_direct():
    """Test GPT-5-mini with increasingly simple prompts to find what works"""
    
    print("🔍 Debug GPT-5-mini Empty Response Issue")
    print("=" * 50)
    
    # Check environment
    print(f"OPENAI_DEPLOYMENT_NAME: {os.environ.get('OPENAI_DEPLOYMENT_NAME', 'NOT SET')}")
    print(f"OPENAI_API_KEY: {'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")
    print(f"OPENAI_API_BASE: {os.environ.get('OPENAI_API_BASE', 'NOT SET')}")
    print()
    
    # Create LLM instance
    try:
        llm = FallbackChatLLM(model_name="gpt-5-mini", temperature=0.1)
        print("✅ FallbackChatLLM created successfully")
    except Exception as e:
        print(f"❌ Failed to create FallbackChatLLM: {e}")
        return
    
    # Test 1: Ultra-simple prompt
    print("\n🧪 TEST 1: Ultra-simple prompt")
    simple_prompt = "Generate 10 numbers: 20.1, 20.2, 20.3, and continue with 7 more realistic temperature values."
    
    try:
        response = llm.generate(simple_prompt)
        print(f"📝 Response length: {len(response)} characters")
        print(f"📄 Response: '{response}'")
        if len(response) == 0:
            print("❌ Empty response!")
        else:
            print("✅ Got response!")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Our optimized prompt
    print("\n🧪 TEST 2: Our GPT-5-mini optimized prompt")
    try:
        optimized_prompt = get_gpt5mini_optimized_prompt("NAVE_TEMP_01", "°C", 12)
        print(f"🔧 Optimized prompt (first 200 chars): {optimized_prompt[:200]}...")
        
        response = llm.generate(optimized_prompt)
        print(f"📝 Response length: {len(response)} characters")
        print(f"📄 Response: '{response}'")
        if len(response) == 0:
            print("❌ Empty response!")
        else:
            print("✅ Got response!")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Minimal prompt
    print("\n🧪 TEST 3: Minimal prompt")
    minimal_prompt = "20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9, 21.0"
    
    try:
        response = llm.generate(minimal_prompt)
        print(f"📝 Response length: {len(response)} characters")
        print(f"📄 Response: '{response}'")
        if len(response) == 0:
            print("❌ Empty response!")
        else:
            print("✅ Got response!")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: Different system message
    print("\n🧪 TEST 4: Test with different system message")
    test_prompt = "Please generate exactly 10 temperature values like: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9, 21.0"
    
    try:
        response = llm.generate(test_prompt)
        print(f"📝 Response length: {len(response)} characters")
        print(f"📄 Response: '{response}'")
        if len(response) == 0:
            print("❌ Empty response!")
        else:
            print("✅ Got response!")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_gpt5mini_direct()