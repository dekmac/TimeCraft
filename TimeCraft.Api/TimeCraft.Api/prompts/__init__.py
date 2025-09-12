"""
Prompt configuration and management for TimeCraft API.

This module provides centralized access to all prompt templates and configurations.
"""

from .tag_generation import (
    create_tag_generation_prompt,
    create_tag_reflection_prompt,
    create_tag_regeneration_prompt
)

from .timeseries_generation import (
    create_timeseries_generation_prompt,
    create_timeseries_reflection_prompt,
    create_timeseries_improvement_prompt,
    create_scenario_refinement_system_prompt,
    create_scenario_refinement_user_prompt,
    create_fallback_scenario_prompt
)

from .device_analysis import (
    create_device_analysis_prompt,
    create_basic_device_prompt,
    create_fallback_device_prompt,
    get_device_type_mapping,
    get_application_domain_mapping
)


class PromptConfig:
    """Configuration class for prompt management."""
    
    # Prompt types
    TAG_GENERATION = "tag_generation"
    TAG_REFLECTION = "tag_reflection"
    TAG_REGENERATION = "tag_regeneration"
    TIMESERIES_GENERATION = "timeseries_generation"
    TIMESERIES_REFLECTION = "timeseries_reflection"
    TIMESERIES_IMPROVEMENT = "timeseries_improvement"
    SCENARIO_REFINEMENT = "scenario_refinement"
    DEVICE_ANALYSIS = "device_analysis"
    
    # Default parameters
    DEFAULT_MAX_RETRIES = 2
    DEFAULT_TIMEOUT = 120
    DEFAULT_TEMPERATURE = 0.1
    
    # Reflection settings
    REFLECTION_ENABLED = True
    REFLECTION_MAX_RETRIES = 2
    REFLECTION_DELAY_SECONDS = 5


class PromptManager:
    """Centralized prompt management for the TimeCraft API."""
    
    def __init__(self):
        self.config = PromptConfig()
        self.device_type_mapping = get_device_type_mapping()
        self.application_domain_mapping = get_application_domain_mapping()
    
    # Tag Generation Prompts
    def get_tag_generation_prompt(self, description: str, num_tags: int) -> str:
        """Get the tag generation prompt."""
        return create_tag_generation_prompt(description, num_tags)
    
    def get_tag_reflection_prompt(self, original_description: str, generated_tags: list, num_tags: int) -> str:
        """Get the tag reflection prompt."""
        return create_tag_reflection_prompt(original_description, generated_tags, num_tags)
    
    def get_tag_regeneration_prompt(self, description: str, num_tags: int, feedback: str) -> str:
        """Get the tag regeneration prompt."""
        return create_tag_regeneration_prompt(description, num_tags, feedback)
    
    # Timeseries Generation Prompts
    def get_timeseries_generation_prompt(self, tag_name: str, description: str, sequence_length: int,
                                       scenario: str = None, time_period: str = None, device_prompt: str = "") -> str:
        """Get the timeseries generation prompt."""
        return create_timeseries_generation_prompt(tag_name, description, sequence_length, scenario, time_period, device_prompt)
    
    def get_timeseries_reflection_prompt(self, tag_name: str, description: str, generated_values: list, sequence_length: int) -> str:
        """Get the timeseries reflection prompt."""
        return create_timeseries_reflection_prompt(tag_name, description, generated_values, sequence_length)
    
    def get_timeseries_improvement_prompt(self, tag_name: str, description: str, sequence_length: int, feedback: str) -> str:
        """Get the timeseries improvement prompt."""
        return create_timeseries_improvement_prompt(tag_name, description, sequence_length, feedback)
    
    # Scenario Refinement Prompts
    def get_scenario_refinement_prompts(self, scenario: str, sequence_length: int = 168) -> tuple:
        """Get the scenario refinement system and user prompts."""
        system_prompt = create_scenario_refinement_system_prompt()
        user_prompt = create_scenario_refinement_user_prompt(scenario, sequence_length)
        return system_prompt, user_prompt
    
    def get_fallback_scenario_prompt(self, scenario: str, sequence_length: int = 168) -> str:
        """Get the fallback scenario prompt."""
        return create_fallback_scenario_prompt(scenario, sequence_length)
    
    # Device Analysis Prompts
    def get_device_analysis_prompt(self, tag_name: str, device_info: dict) -> str:
        """Get the device analysis prompt."""
        return create_device_analysis_prompt(tag_name, device_info)
    
    def get_basic_device_prompt(self, device_info: dict, tag_name: str) -> str:
        """Get the basic device prompt."""
        return create_basic_device_prompt(device_info, tag_name)
    
    def get_fallback_device_prompt(self, device_info: dict, tag_name: str) -> str:
        """Get the fallback device prompt."""
        return create_fallback_device_prompt(device_info, tag_name)
    
    # Helper Methods
    def detect_device_type_from_tag(self, tag_name: str) -> dict:
        """Detect device type and parameters from tag name."""
        tag_upper = tag_name.upper()
        
        # Check each device type mapping
        for device_type, mapping in self.device_type_mapping.items():
            if any(keyword in tag_upper for keyword in mapping['keywords']):
                device_info = mapping['info'].copy()
                device_info['application'] = self._detect_application_from_tag(tag_upper)
                return device_info
        
        # Generic catch-all
        return {
            'type': 'generic',
            'measurement': 'process parameter',
            'units': 'various',
            'typical_range': 'application dependent',
            'application': self._detect_application_from_tag(tag_upper)
        }
    
    def _detect_application_from_tag(self, tag_upper: str) -> str:
        """Detect the application domain from tag name."""
        for domain, keywords in self.application_domain_mapping.items():
            if any(keyword in tag_upper for keyword in keywords):
                return domain
        return 'general_industrial'


# Global prompt manager instance
prompt_manager = PromptManager()


# Convenience functions for backward compatibility
def get_tag_generation_prompt(description: str, num_tags: int) -> str:
    """Convenience function for tag generation prompt."""
    return prompt_manager.get_tag_generation_prompt(description, num_tags)


def get_tag_reflection_prompt(original_description: str, generated_tags: list, num_tags: int) -> str:
    """Convenience function for tag reflection prompt."""
    return prompt_manager.get_tag_reflection_prompt(original_description, generated_tags, num_tags)


def get_timeseries_generation_prompt(tag_name: str, description: str, sequence_length: int,
                                   scenario: str = None, time_period: str = None, device_prompt: str = "") -> str:
    """Convenience function for timeseries generation prompt."""
    return prompt_manager.get_timeseries_generation_prompt(tag_name, description, sequence_length, scenario, time_period, device_prompt)


def get_timeseries_reflection_prompt(tag_name: str, description: str, generated_values: list, sequence_length: int) -> str:
    """Convenience function for timeseries reflection prompt."""
    return prompt_manager.get_timeseries_reflection_prompt(tag_name, description, generated_values, sequence_length)


def detect_device_type_from_tag(tag_name: str) -> dict:
    """Convenience function for device type detection."""
    return prompt_manager.detect_device_type_from_tag(tag_name)