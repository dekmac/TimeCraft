"""
Tag generation prompt templates for TimeCraft API.

This module contains all prompts related to generating and refining sensor tag names.
"""

from typing import List


def create_tag_generation_prompt(description: str, num_tags: int) -> str:
    """Create a sophisticated prompt for realistic domain-specific tag generation."""
    return f"""You are an expert in industrial monitoring and sensor systems. Generate {num_tags} realistic sensor tag names for the following monitoring scenario.

MONITORING SCENARIO: {description}

INSTRUCTIONS:
1. Analyze the scenario description to understand the industry/domain (e.g., manufacturing, food processing, chemical plant, HVAC, power generation, etc.)
2. Generate sensor tag names that are appropriate for that specific domain
3. Use realistic industrial naming conventions and sensor types for that industry

GENERAL NAMING CONVENTIONS:
- Format: [LOCATION]_[MEASUREMENT_TYPE]_[ID] or [EQUIPMENT]_[PARAMETER]_[INSTANCE]
- Use clear, descriptive abbreviations
- Include equipment/location identifiers relevant to the scenario
- Use consistent numbering/naming schemes

SENSOR TYPES TO CONSIDER BASED ON DOMAIN:
- Temperature sensors (TEMP, TI, TE)
- Pressure sensors (PRESS, PI, PE) 
- Flow meters (FLOW, FI, FE)
- Level sensors (LEVEL, LI, LE)
- Speed/RPM sensors (SPEED, SI, SE)
- Vibration monitors (VIB, VI, VE)
- Current/Power meters (AMP, PI, PE)
- pH/Chemical sensors (PH, AI, AE)
- Humidity sensors (HUM, HI, HE)
- Position/Valve sensors (POS, ZI, ZE)

DOMAIN-SPECIFIC EXAMPLES:
- Food Processing: PASTEURIZER_TEMP_01, TANK_LEVEL_RAW_MILK, FILLING_LINE_SPEED_02
- Manufacturing: MOTOR_VIBRATION_A1, HYDRAULIC_PRESS_01, CONVEYOR_SPEED_LINE3
- HVAC: CHILLER_TEMP_SUPPLY, AHU_FLOW_RATE_01, ROOM_HUMIDITY_ZONE2
- Chemical Plant: REACTOR_TEMP_R101, DISTILLATION_PRESS_C201, PUMP_FLOW_P301

REQUIREMENTS:
1. Generate exactly {num_tags} realistic tag names
2. Make tags specific to the scenario described
3. Use diverse measurement types appropriate for the domain
4. Include varied equipment/location names relevant to the scenario
5. Use realistic industrial abbreviations and identifiers
6. Ensure tag names reflect the actual monitoring needs of that industry
7. Be creative but realistic - think about what sensors would actually be needed

Return only the tag names separated by commas, no additional text or explanations."""


def create_tag_reflection_prompt(original_description: str, generated_tags: List[str], 
                                num_tags: int) -> str:
    """Create a prompt for the LLM to reflect on and assess its tag generation."""
    tags_str = ", ".join(generated_tags)
    
    return f"""You are an expert in industrial monitoring systems. Please assess the quality of these generated sensor tag names.

ORIGINAL REQUEST: Generate {num_tags} realistic sensor tag names for: "{original_description}"

GENERATED TAGS: {tags_str}

ASSESSMENT CRITERIA:
1. RELEVANCE: Do the tags match the industrial domain described?
2. REALISM: Are these actual sensor types used in this industry?
3. NAMING CONVENTION: Do they follow proper industrial tag naming?
4. QUANTITY: Are there exactly {num_tags} tags?
5. DIVERSITY: Do they represent different measurement types?
6. SPECIFICITY: Are they specific to the described scenario?

ASSESSMENT:
- Rate each criterion (1-10): Relevance, Realism, Naming, Quantity, Diversity, Specificity
- Overall Quality Score (1-10):
- Issues Found: [List any problems]
- Improvements Needed: [Specific suggestions]

Is this output ACCEPTABLE (YES/NO)? If NO, provide better tag names.

FORMAT:
RELEVANCE: [score]/10
REALISM: [score]/10 
NAMING: [score]/10
QUANTITY: [score]/10
DIVERSITY: [score]/10
SPECIFICITY: [score]/10
OVERALL: [score]/10
ISSUES: [list issues]
IMPROVEMENTS: [suggestions]
ACCEPTABLE: YES/NO
BETTER_TAGS: [only if NO - provide improved tags]"""


def create_tag_regeneration_prompt(description: str, num_tags: int, feedback: str) -> str:
    """Create a prompt for regenerating tags based on reflection feedback."""
    return f"""Based on the reflection feedback, generate exactly {num_tags} BETTER sensor tag names for: "{description}"

FEEDBACK FROM REFLECTION:
{feedback}

REQUIREMENTS:
1. Address all issues identified in the feedback
2. Generate exactly {num_tags} improved tag names
3. Ensure they are realistic and industry-appropriate
4. Follow proper industrial naming conventions
5. Make them specific to the scenario described

Return only the improved tag names separated by commas, no additional text or explanations."""