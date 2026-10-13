"""
Deterministic mock inference adapter; external providers are not implemented.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Ibd Flare Biomarker Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} mock]: No clinical evaluation or language-model inference was performed. Input preview: {prompt[:60]!r}."


class LLMFactory:
    """Creates configured LLM client instances with zero-PHI protection."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Ibd Flare Biomarker Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        if prov in {"ollama", "local", "claude", "anthropic", "openai", "gpt4"}:
            raise NotImplementedError(
                f"Provider {prov!r} is not implemented. Use 'mock' for offline demonstrations."
            )
        raise ValueError(f"Unknown model provider: {provider!r}")
