#!/usr/bin/env python3
"""
Test GPT-5-mini specific prompt formatting - simpler approach
"""

def test_gpt5mini_prompt():
    """Test a much simpler prompt that might work better with GPT-5-mini."""
    
    # Simplified prompt that's very direct
    simple_prompt = """Generate exactly 288 temperature values in Celsius for indoor building monitoring over 24 hours.

Requirements:
- Values between 18-26°C  
- Daily pattern: cool night → gradual rise → peak afternoon → gradual fall
- Smooth natural variations only
- Format: comma-separated numbers only

Example start: 19.2, 19.1, 19.0, 18.9, 18.8, 19.0, 19.2, 19.5

Your response should start immediately with numbers, no text before:"""

    print("SIMPLE GPT-5-MINI PROMPT:")
    print("=" * 80)
    print(simple_prompt)
    print("=" * 80)
    print(f"Length: {len(simple_prompt)} characters")
    
    # Even simpler version
    ultra_simple = """Generate 288 temperature readings: 19.2, 19.1, 19.0, 18.9, 18.8, 19.0, 19.2, 19.5, 19.8, 20.1, 20.4, 20.7, 21.0, 21.3, 21.6, 21.9, 22.2, 22.5, 22.8, 23.1, 23.4, 23.7, 24.0, 24.2, 24.4, 24.6, 24.7, 24.8, 24.9, 25.0, 25.0, 24.9, 24.8, 24.7, 24.5, 24.3, 24.0, 23.7, 23.4, 23.1, 22.8, 22.5, 22.2, 21.9, 21.6, 21.3, 21.0, 20.7, 20.4, 20.1, 19.8, 19.5, 19.2, 19.0, and continue this pattern for 288 total values covering 24 hours of realistic building temperature data."""

    print("\nULTRA-SIMPLE GPT-5-MINI PROMPT:")
    print("=" * 80)
    print(ultra_simple)
    print("=" * 80)
    print(f"Length: {len(ultra_simple)} characters")

if __name__ == "__main__":
    test_gpt5mini_prompt()