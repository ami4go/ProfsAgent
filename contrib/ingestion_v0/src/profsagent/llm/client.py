"""
Unified LLM API Client for ProfsAgent.

Provides a unified interface to call frontier LLM APIs (Google Gemini, OpenAI, Anthropic)
or local models (Ollama), returning validated structured outputs conforming to Pydantic models.
"""

import os
from typing import Any, TypeVar
from pydantic import BaseModel
from profsagent.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Wrapper around LLM APIs for structured extraction and evaluation."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or settings.LLM_MODEL

    def is_configured(self) -> bool:
        """Checks if an API key is available for the configured provider."""
        if self.provider == "gemini":
            return bool(settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY"))
        elif self.provider == "openai":
            return bool(settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))
        elif self.provider == "anthropic":
            return bool(settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY"))
        return False

    def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
    ) -> T | None:
        """
        Calls the LLM API and parses the response directly into the target Pydantic schema.
        Falls back gracefully if the API key is not configured.
        """
        if not self.is_configured():
            return None

        # Example implementation for Google Gemini API
        if self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY"))
                model_inst = genai.GenerativeModel(
                    model_name=self.model,
                    system_instruction=system_instruction,
                )
                response = model_inst.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                    ),
                )
                return response_schema.model_validate_json(response.text)
            except Exception as err:
                print(f"[LLM API Warning] Gemini call failed: {err}")
                return None

        # Example implementation for OpenAI API
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))
                response = client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_instruction or "You are an academic course design assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    response_format=response_schema,
                )
                return response.choices[0].message.parsed
            except Exception as err:
                print(f"[LLM API Warning] OpenAI call failed: {err}")
                return None

        return None
