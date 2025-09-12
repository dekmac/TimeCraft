#!/usr/bin/env python3
"""
Example script demonstrating the refactored TimeCraft prompt system.

This script shows how to use the new modular prompt system for generating
tag names and time series data.
"""

import sys
import os

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Demonstrate the new prompt system."""
    print("🏭 TimeCraft Prompt System Demo")
    print("=" * 50)
    
    try:
        # Import the prompt system
        from prompts import prompt_manager, get_tag_generation_prompt
        from prompts.keyword_fallbacks import generate_tags_from_keywords
        
        print("✅ Successfully imported prompt system")
        
        # Example 1: Tag Generation
        print("\n1️⃣  Tag Generation Example")
        print("-" * 30)
        
        description = "dairy processing plant with pasteurization and homogenization"
        num_tags = 5
        
        # Generate prompt
        prompt = prompt_manager.get_tag_generation_prompt(description, num_tags)
        print(f"📝 Generated prompt (first 200 chars):")
        print(f"   {prompt[:200]}...")
        
        # Generate fallback tags
        fallback_tags = generate_tags_from_keywords(description, num_tags)
        print(f"🏷️  Fallback tags: {fallback_tags}")
        
        # Example 2: Device Detection
        print("\n2️⃣  Device Type Detection Example")
        print("-" * 35)
        
        tag_names = [
            "PASTEURIZER_TEMP_01",
            "MOTOR_VIBRATION_A1", 
            "REACTOR_PRESSURE_R101",
            "CHILLER_FLOW_RATE_01"
        ]
        
        for tag_name in tag_names:
            device_info = prompt_manager.detect_device_type_from_tag(tag_name)
            print(f"🔧 {tag_name}")
            print(f"   Type: {device_info.get('type', 'unknown')}")
            print(f"   Measurement: {device_info.get('measurement', 'unknown')}")
            print(f"   Application: {device_info.get('application', 'unknown')}")
            print()
        
        # Example 3: Time Series Generation Prompt
        print("3️⃣  Time Series Generation Example")
        print("-" * 35)
        
        tag_name = "PASTEURIZER_TEMP_01"
        description = "dairy processing pasteurization system"
        sequence_length = 24
        
        # Get device-specific prompt
        device_info = prompt_manager.detect_device_type_from_tag(tag_name)
        device_prompt = prompt_manager.get_basic_device_prompt(device_info, tag_name)
        
        # Generate time series prompt
        ts_prompt = prompt_manager.get_timeseries_generation_prompt(
            tag_name, description, sequence_length, device_prompt=device_prompt
        )
        
        print(f"📊 Time series prompt for {tag_name} (first 300 chars):")
        print(f"   {ts_prompt[:300]}...")
        
        # Example 4: Configuration
        print("\n4️⃣  Configuration Example")
        print("-" * 25)
        
        config = prompt_manager.config
        print(f"🔧 Max Retries: {config.DEFAULT_MAX_RETRIES}")
        print(f"🔧 Timeout: {config.DEFAULT_TIMEOUT}s")
        print(f"🔧 Reflection Enabled: {config.REFLECTION_ENABLED}")
        print(f"🔧 Temperature: {config.DEFAULT_TEMPERATURE}")
        
        print("\n✅ Demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the TimeCraft.Api directory")
        return 1
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)