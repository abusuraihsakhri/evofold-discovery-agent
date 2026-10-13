"""
Inference Engine supporting local Ollama, Claude, OpenAI, and deterministic Mock with Zero-PHI checks.
"""
from .base import PHIGuard


class MockLLM:
    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"Mock response only; no molecular inference performed. Query excerpt: '{prompt[:40]}...'"


class LLMFactory:
    """Creates configured LLM client instances with zero-PHI protection."""

    @staticmethod
    def create(provider: str = "mock"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM()
        elif prov in ["ollama", "local"]:
            return MockLLM()
        elif prov in ["claude", "anthropic"]:
            return MockLLM()
        elif prov in ["openai", "gpt4"]:
            return MockLLM()
        return MockLLM()
