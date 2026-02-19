from ai.rag import RAGProductChain
from ai.vector_db import EmbeddingService, FAISSVectorDB, VectorDBManager
from ai.providers.langchain_service import OpenAILangChainService


class DummyLLM:
    def __call__(self, messages):
        # messages may be a list with prompt string
        prompt = messages[0] if isinstance(messages, list) else messages
        return type("R", (), {"content": "Recomendação: escolha o produto A porque é mais barato."})


def test_rag_retrieve_and_generate():
    # small dataset
    produtos = [
        {"nome": "Notebook Dell 8GB", "preco": 2500},
        {"nome": "Notebook Dell 16GB", "preco": 3200},
        {"nome": "Notebook HP 8GB", "preco": 2300},
    ]

    emb = EmbeddingService(model_name="all-MiniLM-L6-v2")
    faiss_db = FAISSVectorDB(dimension=emb.dim)
    vman = VectorDBManager(emb, vector_db=faiss_db)
    vman.index_products(produtos)

    llm = DummyLLM()
    # create a minimal OpenAILangChainService-like wrapper: we use DummyLLM directly
    class LLMServiceWrapper:
        def __init__(self, client):
            self.client = client
        def __call__(self, messages):
            return self.client(messages)

    service = LLMServiceWrapper(llm)
    rag = RAGProductChain(service, vman)

    out = rag.retrieve_and_generate("notebook dell 16gb", k=2)
    assert "resposta" in out
    assert isinstance(out["hits"], list)
