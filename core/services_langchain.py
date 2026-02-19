# Deprecated shim: re-export LangChain wrapper from ai.providers
import warnings
warnings.warn("core.services_langchain is deprecated; use ai.providers.langchain_service instead", DeprecationWarning)
from ai.providers.langchain_service import OpenAILangChainService

__all__ = ["OpenAILangChainService"]
