from config.config import ConversationManager


class MockRAG:
    def __init__(self):
        self.called = False

    def retrieve_and_generate(self, query: str, k: int = 5):
        self.called = True
        return {"resposta": f"RAG recomenda produto para: {query}", "hits": [{"nome": "Produto X", "preco": 100}],}


def test_modo_buscar_usa_rag():
    # Injeta um RAG mock no ConversationManager
    cm = ConversationManager(llm=None)
    cm.rag = MockRAG()

    uid = "u_rag"
    cm.iniciar_conversa(uid, "Teste")
    cm.processar_mensagem(uid, "1")  # escolhe modo buscar

    res = cm.processar_mensagem(uid, "Quero notebook Dell até R$ 3000 com 16GB e SSD")

    assert res.get("executar_busca") is True
    assert "RAG recomenda" in res.get("resposta")
    assert res.get("hits") and isinstance(res.get("hits"), list)
