#!/usr/bin/env python3
"""
Quick test to debug GPT-5-mini zero values issue
"""
import sys
import os

# Add the API directory to Python path
sys.path.append('TimeCraft.Api/TimeCraft.Api')
sys.path.append('TimeCraft.Api/TimeCraft.Api/api')

try:
    from helpers import LLMHelper
except ImportError:
    try:
        from api.helpers import LLMHelper
    except ImportError:
        print("❌ Cannot import LLMHelper - check Python path")

def test_gpt5_mini_response():
    """Test what GPT-5-mini is actually returning."""
    
    # Simple test prompts
    test_prompts = [
        # Ultra simple
        "Generate 10 numbers: 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.0",
        
        # Simple temperature
        "Generate exactly 10 temperature values in °C: 19.2, 19.1, 19.0, 18.9, 18.8, 19.0, 19.2, 19.5, 19.8, 20.1",
        
        # Current format
        """Generate 10 realistic sensor values for: temperature (°C)

OUTPUT FORMAT:
Your response must be ONLY comma-separated numbers. Start with a number, not text.

CORRECT: 23.4, 24.1, 23.8, 24.5, 23.9, 24.2""",
    ]
    
    # Initialize LLM helper
    try:
        llm = LLMHelper()
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n{'='*80}")
            print(f"TEST {i}: PROMPT")
            print(f"{'='*80}")
            print(prompt)
            print(f"{'='*80}")
            print(f"RESPONSE:")
            print(f"{'='*80}")
            
            try:
                response = llm.generate(prompt)
                print(f"Raw response: '{response}'")
                print(f"Length: {len(response)} chars")
                print(f"First 200 chars: {response[:200]}...")
                
                # Try to extract numbers
                import re
                numbers = []
                for part in re.split(r'[,;\s]+', response):
                    try:
                        numbers.append(float(part.strip()))
                    except ValueError:
                        continue
                
                print(f"Extracted numbers: {len(numbers)} values")
                if numbers:
                    print(f"First few: {numbers[:10]}")
                else:
                    print("❌ NO NUMBERS EXTRACTED")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("="*80)
        
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")

if __name__ == "__main__":
    test_gpt5_mini_response()