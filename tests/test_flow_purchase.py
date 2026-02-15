from config.config import ConversationManager


class MockRAGForFlow:
    def retrieve_and_generate(self, query: str, k: int = 5):
        hits = [
            {"nome": "Notebook Dell 8GB", "preco": 2500, "loja": "Loja A", "specs": "8GB RAM, 256GB SSD, Intel i5"},
            {"nome": "Notebook Dell 16GB", "preco": 3200, "loja": "Loja B", "specs": "16GB RAM, 512GB SSD, Intel i7"},
        ]
        return {"resposta": "Encontrei 2 produtos.", "hits": hits}


def test_purchase_flow():
    cm = ConversationManager(llm=None)
    cm.rag = MockRAGForFlow()

    uid = "user_flow"
    # Start
    intro = cm.iniciar_conversa(uid, "Flavio")
    # Choose buscar
    r1 = cm.processar_mensagem(uid, "1")
    assert "BUSCAR" in r1["resposta"].upper()

    # Send detailed search
    r2 = cm.processar_mensagem(uid, "Quero notebook Dell até R$3000 com 16GB")
    assert r2.get("estado") == "aguardando_selecao_produto"
    assert "1)" in r2.get("resposta")

    # Select product 2
    r3 = cm.processar_mensagem(uid, "2")
    assert r3.get("estado") == "aguardando_confirmacao_adicao"
    assert "Especificações" in r3.get("resposta") or "Especificações" in r3.get("resposta")

    # Confirm add
    r4 = cm.processar_mensagem(uid, "sim")
    assert r4.get("carrinho") and len(r4.get("carrinho")) == 1
    assert "adicionado" in r4.get("resposta").lower()

    # Finalize
    r5 = cm.processar_mensagem(uid, "4")  # go to finalize
    r6 = cm.processar_mensagem(uid, "Quero finalizar a compra")
    # Should indicate manual checkout
    assert r6.get("manual_checkout") is True or "manual" in r6.get("resposta").lower()
