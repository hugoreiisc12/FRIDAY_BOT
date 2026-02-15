from typing import List, Dict, Any
from core.services_langchain import OpenAILangChainService
from ai.vector_db import VectorDBManager, EmbeddingService


class RAGProductChain:
    def __init__(self, llm_service: OpenAILangChainService, vector_manager: VectorDBManager):
        self.llm_service = llm_service
        self.vector_manager = vector_manager

    def index_products(self, produtos: List[Dict[str, Any]]):
        self.vector_manager.index_products(produtos)

    def retrieve(self, query: str, k: int = 5):
        return self.vector_manager.search_semantic(query, k=k)

    def retrieve_and_generate(self, query: str, k: int = 5) -> Dict[str, Any]:
        # 1) retrieve
        hits = self.retrieve(query, k=k)
        if not hits:
            return {"resposta": "Não encontrei produtos relevantes.", "hits": []}

        # 2) build prompt
        snippets = []
        for h in hits:
            p = h["produto"] if isinstance(h, dict) and "produto" in h else h
            name = p.get("nome") if isinstance(p, dict) else str(p)
            snippets.append(f"- {name}")

        prompt = f"Encontrei os seguintes produtos para '{query}':\n" + "\n".join(snippets) + "\n\nCom base nisso, recomende o melhor produto e explique por que."

        # 3) call LLM (via service wrapper)
        try:
            resp = self.llm_service([prompt])
            text = resp.content if hasattr(resp, "content") else str(resp)
        except Exception:
            text = "Desculpe, não foi possível gerar recomendação agora."

        return {"resposta": text, "hits": hits}
