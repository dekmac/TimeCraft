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
    text_description: str
    model_name: Optional[str] = "gpt-4o"
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
    text_description: str
    num_tags: Optional[int] = 5
    sequence_length: Optional[int] = 168
    model_name: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.0
    openai_api_base: Optional[str] = None
    openai_api_version: Optional[str] = None
    openai_api_type: Optional[str] = None


class TagGenerationRequest(BaseModel):
    """Request model for tag name generation."""
    text_description: str
    num_tags: Optional[int] = 5
    model_name: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.0


class TagGenerationResponse(BaseModel):
    """Response model for tag name generation."""
    status: str
    message: str
    text_description: str
    num_tags: int
    tags: List[str]
    generation_method: str


class SingleTimeSeriesRequest(BaseModel):
    """Request model for single timeseries generation."""
    tag_name: str
    text_description: str
    sequence_length: Optional[int] = 168
    tag_index: Optional[int] = 0
    model_name: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.0


class SingleTimeSeriesResponse(BaseModel):
    """Response model for single timeseries generation."""
    status: str
    message: str
    tag_name: str
    text_description: str
    sequence_length: int
    timeseries: List[float]
    generation_method: str


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: str