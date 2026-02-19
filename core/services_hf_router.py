# Deprecated shim: re-export HuggingFace Router provider from ai.providers
import warnings
warnings.warn("core.services_hf_router is deprecated; use ai.providers.hf_router_service instead", DeprecationWarning)
from ai.providers.hf_router_service import HuggingFaceRouterService

__all__ = ["HuggingFaceRouterService"]