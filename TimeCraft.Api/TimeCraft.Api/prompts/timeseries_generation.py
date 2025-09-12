"""
Time series data generation prompt templates for TimeCraft API.

This module contains all prompts related to generating and refining time series data.
"""

from typing import List


def create_timeseries_generation_prompt(
    tag_name: str,
    description: str,
    sequence_length: int,
    scenario: str = None,
    time_period: str = None,
    device_prompt: str = ""
) -> str:
    """
    Create a sophisticated prompt for realistic domain-aware timeseries generation.
    """
    scenario_text = f"\nScenario Context: {scenario}" if scenario else ""
    time_period_text = f"\nTime Period: {time_period}" if time_period else ""
    
    return f"""You are generating realistic time series data for an industrial monitoring system.

SENSOR DETAILS:
Tag Name: {tag_name}
System Description: {description}{scenario_text}{time_period_text}

{device_prompt}

DATA GENERATION REQUIREMENTS:
1. Generate exactly {sequence_length} numerical values
2. Include realistic measurement characteristics:
   - Appropriate noise levels and measurement precision
   - Natural drift and baseline variations
   - Occasional data spikes or anomalies (5-10% of readings)
   - Environmental influences (temperature, humidity, pressure)
3. Temporal patterns:
   - Industry-appropriate daily/operational cycles
   - Random variations with realistic autocorrelation
   - Gradual trends (equipment aging, process drift)
   - Event responses (load changes, environmental factors)
4. Data quality simulation:
   - 2-3% outliers or measurement errors
   - Occasional brief periods of elevated/reduced activity
   - Realistic sensor behavior (not perfectly smooth)
5. Engineering realism:
   - Values should reflect real-world industrial measurements
   - Include both positive and negative values where appropriate
   - Show process response to operational and environmental conditions

OUTPUT FORMAT:
Return exactly {sequence_length} comma-separated numerical values representing sequential measurements.
No additional text, explanations, or formatting - just the raw numerical data."""


def create_timeseries_reflection_prompt(tag_name: str, description: str, 
                                       generated_values: List[float], 
                                       sequence_length: int) -> str:
    """Create a prompt for the LLM to reflect on timeseries generation quality."""
    values_preview = ", ".join([f"{v:.3f}" for v in generated_values[:10]])
    if len(generated_values) > 10:
        values_preview += f"... (showing first 10 of {len(generated_values)} values)"
    
    stats = {
        'min': min(generated_values),
        'max': max(generated_values),
        'avg': sum(generated_values) / len(generated_values),
        'range': max(generated_values) - min(generated_values)
    }
    
    return f"""You are an expert in industrial sensor data and time series analysis. Assess the quality of this generated sensor data.

SENSOR TAG: {tag_name}
SYSTEM DESCRIPTION: {description}
REQUESTED LENGTH: {sequence_length}
GENERATED LENGTH: {len(generated_values)}

GENERATED DATA PREVIEW: {values_preview}

STATISTICS:
- Min: {stats['min']:.3f}
- Max: {stats['max']:.3f}  
- Average: {stats['avg']:.3f}
- Range: {stats['range']:.3f}

ASSESSMENT CRITERIA:
1. REALISM: Are values realistic for this sensor type?
2. VARIABILITY: Does data show appropriate variation/noise?
3. PATTERNS: Are there realistic temporal patterns?
4. SCALE: Are the value ranges appropriate?
5. COMPLETENESS: Is the data length correct?
6. PHYSICS: Does the data follow physical constraints?

ASSESSMENT:
- Rate each criterion (1-10): Realism, Variability, Patterns, Scale, Completeness, Physics
- Overall Quality Score (1-10):
- Issues Found: [List problems with the data]
- Physics Violations: [Any unrealistic values or patterns]

Is this data ACCEPTABLE (YES/NO)? 

FORMAT:
REALISM: [score]/10
VARIABILITY: [score]/10
PATTERNS: [score]/10
SCALE: [score]/10
COMPLETENESS: [score]/10
PHYSICS: [score]/10
OVERALL: [score]/10
ISSUES: [list issues]
VIOLATIONS: [physics problems]
ACCEPTABLE: YES/NO"""


def create_timeseries_improvement_prompt(tag_name: str, description: str, 
                                       sequence_length: int, feedback: str) -> str:
    """Create a prompt for improving timeseries based on reflection feedback."""
    return f"""Based on reflection feedback, generate IMPROVED time series data for:

SENSOR TAG: {tag_name}
SYSTEM DESCRIPTION: {description}
SEQUENCE LENGTH: {sequence_length}

FEEDBACK FROM REFLECTION:
{feedback}

REQUIREMENTS:
1. Address all issues identified in the feedback
2. Generate exactly {sequence_length} numerical values
3. Ensure realistic sensor behavior and appropriate value ranges
4. Include proper temporal patterns and measurement characteristics
5. Follow physical constraints and engineering principles

Return exactly {sequence_length} comma-separated numerical values representing the improved sensor measurements.
No additional text, explanations, or formatting - just the raw numerical data."""


def create_scenario_refinement_system_prompt() -> str:
    """Create the system prompt for scenario refinement."""
    return (
        "You are an expert prompt engineer for time series data generation. "
        "Given a user's scenario description, rewrite it as a detailed, explicit prompt for an AI timeseries generator. "
        "Extract time periods, events, and tag-specific instructions, and write them as clear requirements. "
        "Make sure the output is suitable for an LLM to generate realistic, scenario-driven timeseries data. "
        "If the user provides a sequence length, include it as the number of data points. "
        "Return only the improved prompt, no explanation."
    )


def create_scenario_refinement_user_prompt(scenario: str, sequence_length: int = 168) -> str:
    """Create the user prompt for scenario refinement."""
    return f"Scenario: {scenario}\n\nNumber of data points: {sequence_length}\n"


def create_fallback_scenario_prompt(scenario: str, sequence_length: int = 168) -> str:
    """Create a fallback scenario prompt when LLM refinement fails."""
    return (
        f"Generate realistic hourly time series data reflecting the scenario and events described.\n"
        f"Number of data points: {sequence_length} (one per hour for a week, H1 = Monday 00:00, H{sequence_length} = Sunday 23:00).\n\n"
        f"Scenario: {scenario}\n\n"
        "Requirements:\n"
        "- Make all time/event instructions explicit and easy for an LLM to follow.\n"
        "- Return only the numerical values for each tag, separated by commas, no additional text."
    )