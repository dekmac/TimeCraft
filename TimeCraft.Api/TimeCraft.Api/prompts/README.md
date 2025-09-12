# TimeCraft API Prompts

This directory contains the refactored prompt templates for the TimeCraft API, organized into modular files for better maintainability and easier editing.

## Directory Structure

```
prompts/
├── __init__.py                 # Main prompt manager and convenience functions
├── tag_generation.py          # Tag name generation prompts
├── timeseries_generation.py   # Time series data generation prompts
├── device_analysis.py         # Device-specific analysis prompts
├── keyword_fallbacks.py       # Keyword-based fallback generation
└── README.md                  # This file
```

## Files Overview

### `__init__.py` - Prompt Manager
The main entry point that provides:
- `PromptManager` class: Centralized prompt management
- `PromptConfig` class: Configuration settings
- Convenience functions for backward compatibility
- Device type detection and application domain mapping

### `tag_generation.py` - Tag Generation Prompts
Contains prompts for:
- `create_tag_generation_prompt()`: Main tag generation prompt
- `create_tag_reflection_prompt()`: Quality assessment prompt
- `create_tag_regeneration_prompt()`: Improvement prompt based on feedback

### `timeseries_generation.py` - Time Series Prompts
Contains prompts for:
- `create_timeseries_generation_prompt()`: Main time series generation
- `create_timeseries_reflection_prompt()`: Quality assessment for time series
- `create_timeseries_improvement_prompt()`: Time series improvement based on feedback
- Scenario refinement prompts for Azure OpenAI integration

### `device_analysis.py` - Device-Specific Prompts
Contains:
- `create_device_analysis_prompt()`: LLM-based device analysis
- `create_basic_device_prompt()`: Simple device prompt
- `create_fallback_device_prompt()`: Enhanced fallback prompt
- Device type mappings and application domain mappings

### `keyword_fallbacks.py` - Fallback Generation
Contains:
- `get_keyword_to_tags_mapping()`: Comprehensive keyword-to-tag mappings
- `generate_tags_from_keywords()`: Keyword-based tag generation
- `get_domain_specific_tags()`: Domain-specific tag collections
- `get_generic_tags()`: Generic industrial tags

## Usage

### Basic Usage
```python
from prompts import prompt_manager

# Generate a tag generation prompt
prompt = prompt_manager.get_tag_generation_prompt("dairy processing plant", 5)

# Generate a timeseries prompt with device analysis
device_info = prompt_manager.detect_device_type_from_tag("PASTEURIZER_TEMP_01")
device_prompt = prompt_manager.get_device_analysis_prompt("PASTEURIZER_TEMP_01", device_info)
ts_prompt = prompt_manager.get_timeseries_generation_prompt(
    "PASTEURIZER_TEMP_01", 
    "dairy processing", 
    24, 
    device_prompt=device_prompt
)
```

### Convenience Functions
```python
from prompts import get_tag_generation_prompt, detect_device_type_from_tag

# Use convenience functions for quick access
prompt = get_tag_generation_prompt("manufacturing facility", 3)
device_info = detect_device_type_from_tag("MOTOR_VIBRATION_A1")
```

### Configuration
```python
from prompts import PromptConfig

# Access configuration settings
config = PromptConfig()
print(f"Max retries: {config.DEFAULT_MAX_RETRIES}")
print(f"Reflection enabled: {config.REFLECTION_ENABLED}")
```

## Customizing Prompts

### Editing Existing Prompts
To modify prompts, edit the appropriate function in the relevant file:

1. **Tag Generation**: Edit `create_tag_generation_prompt()` in `tag_generation.py`
2. **Time Series**: Edit `create_timeseries_generation_prompt()` in `timeseries_generation.py`
3. **Device Analysis**: Edit the device mappings in `device_analysis.py`
4. **Fallbacks**: Edit the keyword mappings in `keyword_fallbacks.py`

### Adding New Prompt Types
1. Create new prompt functions in the appropriate file
2. Add corresponding methods to `PromptManager` in `__init__.py`
3. Update the convenience functions if needed

### Adding New Device Types
1. Add new device mappings to `get_device_type_mapping()` in `device_analysis.py`
2. Add new application domains to `get_application_domain_mapping()`
3. Update keyword fallbacks in `keyword_fallbacks.py` if needed

### Adding New Domains
1. Add domain-specific keywords to `get_keyword_to_tags_mapping()` in `keyword_fallbacks.py`
2. Add domain-specific tag collections to `get_domain_specific_tags()`
3. Update the FallbackChatLLM domain detection in the main handler

## Integration with Main API

The refactored prompts integrate seamlessly with the existing API:

```python
# In timeseries_handlers.py
from ..prompts import prompt_manager

# Replace old function calls
# OLD: prompt = create_tag_generation_prompt(description, num_tags)
# NEW: prompt = prompt_manager.get_tag_generation_prompt(description, num_tags)
```

## Benefits

1. **Modularity**: Each prompt type is in its own file
2. **Maintainability**: Easy to find and edit specific prompts
3. **Reusability**: Centralized prompt management
4. **Consistency**: Standardized prompt structure
5. **Flexibility**: Easy to add new prompt types
6. **Configuration**: Centralized settings management
7. **Fallbacks**: Robust keyword-based fallback system

## Migration Notes

- All existing function calls have been updated to use the new prompt manager
- Backward compatibility is maintained through convenience functions
- The FallbackChatLLM has been updated to use domain-specific tags
- Device type detection has been centralized and improved
- Keyword fallbacks are now more comprehensive and organized