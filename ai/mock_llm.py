from dataclasses import dataclass
from typing import List


@dataclass
class MockResponse:
    content: str


class MockLLM:
    """Mock LLM que responde de forma distinta por modo detectado nas mensagens.

    Não depende de `langchain` para permitir execução local sem dependências.
    """

    def __init__(self):
        pass

    def _detect_mode(self, messages: List):
        # messages: list of objects with .content
        sys = " ".join([getattr(m, "content", "") for m in messages]).lower()
        if "buscar" in sys or "especialista em busca" in sys:
            return "buscar"
        if "comparar" in sys or "analista especialista" in sys:
            return "comparar"
        if "negociar" in sys or "negociador" in sys:
            return "negociar"
        if "finalizar" in sys or "checkout" in sys:
            return "finalizar"
        return "default"

    def _reply_for_mode(self, mode: str, human: str) -> str:
        if mode == "buscar":
            return f"✅ Entendi. Vou buscar produtos relacionados a: {human[:120]}"
        if mode == "comparar":
            return "📊 Posso comparar essas opções. Mande os dois produtos separados por 'vs'."
        if mode == "negociar":
            return "💰 Vou procurar descontos e cupons. Me diga o produto e sua expectativa de preço."
        if mode == "finalizar":
            return "✅ Pronto para finalizar. Confirme o produto e escolha a forma de pagamento: PIX, Cartão ou Boleto."
        return "Estou aqui para ajudar. Pode detalhar mais?"

    def __call__(self, messages: List):
        # Accepts list of messages; returns object with .content
        human_msgs = [getattr(m, "content", "") for m in messages]
        human = " ".join(human_msgs).strip()
        mode = self._detect_mode(messages)
        content = self._reply_for_mode(mode, human)
        return MockResponse(content=content)

    def generate(self, prompt: str):
        # backward-compatible simple generate(prompt) -> string
        return f"MockLLM: processed prompt -> {prompt[:200]}"
