"""Wrapper para usar LangChain ChatOpenAI de forma segura e testável."""
from typing import Any, List
import os

# Import optionally
try:
    from langchain.chat_models import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except Exception:
    ChatOpenAI = None
    LANGCHAIN_AVAILABLE = False


class OpenAILangChainService:
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini", temperature: float = 0.7, max_tokens: int = 250):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not LANGCHAIN_AVAILABLE or ChatOpenAI is None:
            raise RuntimeError("LangChain/ChatOpenAI não disponível. Instale 'langchain' para usar este serviço.")

        self.client = ChatOpenAI(api_key=self.api_key, model=model, temperature=temperature, max_tokens=max_tokens)

    def __call__(self, messages: List[Any]):
        """Chama o cliente LangChain com a lista de mensagens e retorna um objeto com `.content` (compatível com MockLLM)."""
        # Alguns adaptadores de LangChain retornam diferentes estruturas; tentamos adaptar.
        try:
            res = self.client(messages)
            # se res tiver .content, OK
            if hasattr(res, "content"):
                return res
            # se for string
            if isinstance(res, str):
                return type("R", (), {"content": res})
        except Exception:
            # Tentar generate() (mais verboso)
            try:
                gen = self.client.generate(messages)
                # acessar primeira geração
                text = ""
                if hasattr(gen, "generations") and gen.generations:
                    # gen.generations: List[List[Generation]]
                    text = gen.generations[0][0].text
                return type("R", (), {"content": text})
            except Exception as e:
                raise
        # fallback
        return type("R", (), {"content": ""})
