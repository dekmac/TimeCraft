#!/usr/bin/env python3
"""
Test GPT-5-mini with the exact system message used in the API
"""

import os
import sys
sys.path.append('TimeCraft.Api/TimeCraft.Api')

try:
    from api.timeseries_handlers import get_gpt5mini_optimized_prompt
    print("✅ Successfully imported TimeCraft modules")
except ImportError:
    print("❌ Import failed - creating minimal test")

# Manual Azure OpenAI test
try:
    import openai
    from openai import AzureOpenAI
    print("✅ OpenAI imported successfully")
except ImportError as e:
    print(f"❌ OpenAI import failed: {e}")
    sys.exit(1)

def test_system_message_issue():
    """Test if the system message is causing GPT-5-mini to return empty responses"""
    
    print("🔍 Testing System Message Issue with GPT-5-mini")
    print("=" * 60)
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment loaded")
    except:
        pass
    
    # Configure Azure OpenAI
    api_key = os.environ.get('OPENAI_API_KEY')
    api_base = os.environ.get('OPENAI_API_BASE', 'https://dm-bb-test.openai.azure.com')
    api_version = os.environ.get('OPENAI_API_VERSION', '2025-04-01-preview')
    deployment_name = os.environ.get('OPENAI_DEPLOYMENT_NAME', 'gpt-5-mini')
    
    print(f"🔧 Using deployment: {deployment_name}")
    print(f"🔧 API Base: {api_base}")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=api_base
        )
        print("✅ Azure OpenAI client created")
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return
    
    # Test prompts
    test_cases = [
        {
            "name": "Simple request",
            "system": "You are a helpful assistant that returns only the requested data without explanation.",
            "user": "Generate 10 temperature values: 20.1, 20.2, 20.3, and continue with 7 more."
        },
        {
            "name": "Complex timeseries prompt",
            "system": "You are a helpful assistant that returns only the requested data without explanation.",
            "user": """Generate 288 realistic sensor values for: NAVE_TEMP_01 (°C)

SCENARIO: Generate synthetic time-series sensor data for monitoring a historic building (the Sagrada Família in Spain) during tourist season.

TIMESPAN: 24 hours (288 measurements every minute)

TEMPERATURE PATTERNS:
• Daily cycle: Cool night (18-20°C) → gradual morning rise → peak afternoon (24-26°C) → gradual fall
• SMOOTH curves only - NO zigzag, sawtooth, or multiple peaks
• Changes: 0.1-0.3°C per minute, 0.5-2°C per hour maximum
• Thermal mass prevents rapid temperature swings

CRITICAL RULES:
• NO constant values (all identical numbers)
• NO linear progressions (1.0, 1.1, 1.2, 1.3...)
• NO unrealistic patterns (zigzag, sawtooth, random spikes)
• Include natural micro-variations even in stable conditions

OUTPUT FORMAT:
Your response must be ONLY comma-separated numbers. Start with a number, not text.

CORRECT: 23.4, 24.1, 23.8, 24.5, 23.9, 24.2
WRONG: DEVICE TYPE: Temperature Sensor
WRONG: Values: 23.4, 24.1, 23.8"""
        },
        {
            "name": "Alternative system message",
            "system": "You generate only numeric data as requested.",
            "user": "Generate 10 temperature values: 20.1, 20.2, 20.3, and continue with 7 more."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['name']}")
        print(f"🔧 System: {test_case['system'][:50]}...")
        print(f"🔧 User prompt length: {len(test_case['user'])} characters")
        
        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": test_case['system']},
                    {"role": "user", "content": test_case['user']}
                ],
                temperature=0.1,
                max_completion_tokens=2000,
                timeout=30
            )
            
            content = response.choices[0].message.content
            print(f"📝 Response length: {len(content)} characters")
            
            if len(content) == 0:
                print("❌ EMPTY RESPONSE!")
            else:
                print(f"✅ Got response: {content[:100]}...")
                
        except Exception as e:
            print(f"❌ API call failed: {e}")

if __name__ == "__main__":
    test_system_message_issue()