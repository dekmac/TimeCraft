#!/usr/bin/env python3
"""
Test Azure OpenAI LLM for time series generation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api.timeseries_handlers import FallbackChatLLM
    
    # Create the LLM instance with your deployment name
    deployment_name = os.getenv('OPENAI_DEPLOYMENT_NAME', 'gpt-4o')
    chat_llm = FallbackChatLLM(model_name=deployment_name)
    print(f"LLM instance created: {type(chat_llm)}")
    
    # Test with a complex structural monitoring prompt
    prompt = """Generate realistic time series data for a structural vibration sensor monitoring a bridge. 
Create 24 comma-separated values representing vibration amplitude in mm over 24 hours.
Include:
- Base oscillations: 0.1-0.3mm (normal structural movement)
- Traffic peaks: 0.5-1.2mm (during rush hours: 7-9am, 5-7pm)
- Wind effects: gradual increases/decreases
- Night settling: lower values 11pm-6am
Return ONLY numerical values separated by commas."""
    
    print("Testing Azure OpenAI with structural monitoring prompt...")
    
    response = chat_llm.generate(prompt)
    print(f"LLM Response length: {len(response)} characters")
    print(f"LLM Response: {response}")
    
    # Try to parse the response
    if "," in response:
        try:
            values = [float(x.strip()) for x in response.split(",") if x.strip()]
            print(f"✅ Success! Parsed {len(values)} values")
            print(f"📊 Sample values: {values[:8]} (first 8)")
            print(f"📈 Value range: {min(values):.3f}mm to {max(values):.3f}mm")
            
            # Check for realistic patterns
            if len(values) >= 24:
                print("🔍 Analyzing realism:")
                avg = sum(values) / len(values)
                print(f"   Average: {avg:.3f}mm")
                
                # Check for variation
                std_dev = (sum((x - avg) ** 2 for x in values) / len(values)) ** 0.5
                print(f"   Std deviation: {std_dev:.3f}mm")
                
                if std_dev > 0.1:
                    print("✅ Data shows good variation (not flat)")
                else:
                    print("⚠️  Data appears relatively flat")
                    
        except ValueError as e:
            print(f"❌ Error parsing values: {e}")
    else:
        print("❌ Response doesn't contain comma-separated values")
        
except Exception as e:
    print(f"Error testing LLM: {e}")
    import traceback
    traceback.print_exc()
