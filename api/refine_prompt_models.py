from typing import Optional
from pydantic import BaseModel

class RefinePromptRequest(BaseModel):
    scenario: str
    sequence_length: Optional[int] = 168
    # Optionally add more fields if needed

class RefinePromptResponse(BaseModel):
    refined_prompt: str
