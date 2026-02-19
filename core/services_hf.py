# Deprecated shim: re-export HF provider from ai.providers
import warnings
warnings.warn("core.services_hf is deprecated; use ai.providers.hf_service instead", DeprecationWarning)
from ai.providers.hf_service import HuggingFaceService

__all__ = ["HuggingFaceService"]
