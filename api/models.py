"""
Pydantic models for TimeCraft API requests and responses.
"""

from typing import Optional, Dict, List
from pydantic import BaseModel


class TimeSeriesGenerationRequest(BaseModel):
    """Request model for time series generation."""
    dataset_name: str
    prediction_length: Optional[int] = 168
    llm_optimize: Optional[bool] = False


class TextRefinementRequest(BaseModel):
    """Request model for text refinement."""
    initial_text: str
    openai_api_base: Optional[str] = None
    openai_api_version: Optional[str] = None
    openai_api_type: Optional[str] = None
    team_iterations: Optional[int] = 3
    global_iterations: Optional[int] = 2


class TextToTimeSeriesRequest(BaseModel):
    """Request model for text-to-time-series generation using BRIDGE model."""
    text: str
    length: Optional[int] = 168
    frequency: Optional[str] = 'hourly'
    domain: Optional[str] = None
    model_name: Optional[str] = "gpt-4o-2024-05-13"
    temperature: Optional[float] = 0.0
    openai_api_base: Optional[str] = None
    openai_api_version: Optional[str] = None
    openai_api_type: Optional[str] = None


class DomainPromptGenerationRequest(BaseModel):
    """Request model for TimeDP domain prompt-based generation."""
    domain_type: str  # e.g., "finance", "energy", "traffic"
    sequence_length: Optional[int] = 168
    num_samples: Optional[int] = 100
    use_text: Optional[bool] = False
    text_prompt: Optional[str] = None


class TargetAwareGenerationRequest(BaseModel):
    """Request model for TarDiff target-aware generation."""
    target_values: Optional[List[float]] = None
    guidance_strength: Optional[float] = 1.0
    sequence_length: Optional[int] = 168
    num_samples: Optional[int] = 100
    classifier_guidance: Optional[bool] = True


class AggregateTimeSeriesRequest(BaseModel):
    """Request model for aggregate multi-tag time series generation."""
    text: str
    tags: List[str]
    length: Optional[int] = 168
    frequency: Optional[str] = 'hourly'
    domain: Optional[str] = None
    model_name: Optional[str] = "gpt-4o-2024-05-13"
    temperature: Optional[float] = 0.0
    openai_api_base: Optional[str] = None
    openai_api_version: Optional[str] = None
    openai_api_type: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: str