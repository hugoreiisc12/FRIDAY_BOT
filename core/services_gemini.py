# Deprecated shim: re-export Gemini provider from ai.providers
import warnings
warnings.warn("core.services_gemini is deprecated; use ai.providers.gemini_service instead", DeprecationWarning)
from ai.providers.gemini_service import GeminiService

__all__ = ["GeminiService"]