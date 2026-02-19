# Deprecated shim: re-export OpenAI provider from ai.providers
import warnings

warnings.warn("core.services_openai is deprecated; use ai.providers.openai_service instead", DeprecationWarning)

from ai.providers.openai_service import OpenAISimpleService  # re-export

__all__ = ["OpenAISimpleService"]
