# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import openai
import os
from pydantic import BaseModel
from typing import List, Optional

# os.environ['OPENAI_API_KEY'] = "xxx"

class ChatLLM(BaseModel):
    model: str = 'gpt-4o'
    temperature: float = 0.0
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    api_type: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided. Please set the OPENAI_API_KEY environment variable or provide it explicitly.")
        
        # Set up OpenAI configuration
        openai.api_key = self.api_key
        
        # Configure for Azure OpenAI if base URL is provided
        if self.api_base is None:
            self.api_base = os.getenv("OPENAI_API_BASE")
        if self.api_version is None:
            self.api_version = os.getenv("OPENAI_API_VERSION", "2024-02-15-preview")
        if self.api_type is None:
            self.api_type = os.getenv("OPENAI_API_TYPE", "openai")
        
        # Apply Azure OpenAI configuration if specified
        if self.api_base:
            openai.api_base = self.api_base
        if self.api_version:
            openai.api_version = self.api_version
        if self.api_type:
            openai.api_type = self.api_type

    def generate(self, prompt: str, stop: List[str] = None):
        response = openai.ChatCompletion.create(
            model=self.model,
            deployment_id=self.model if self.api_type == "azure" else None,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            stop=stop
        )
        return response.choices[0].message.content

