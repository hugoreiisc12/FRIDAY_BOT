import pytest
from ai.conversation_manager import ConversationManager, EstadoBot


from ai.mock_llm import MockLLM


def test_iniciar_conversa():
    llm = MockLLM()
    cm = ConversationManager(llm=llm)
    msg = cm.iniciar_conversa("user123", "Hugo")
    assert "Olá Hugo" in msg


def test_processar_modo_buscar():
    llm = MockLLM()
    cm = ConversationManager(llm=llm)
    # Simulate choosing mode 1
    _ = cm.iniciar_conversa("user123", "Hugo")
    r1 = cm.processar_mensagem("user123", "1")
    assert "BUSCAR PRODUTOS" in r1["resposta"]

    # Now send a detailed query
    r2 = cm.processar_mensagem("user123", "Quero notebook Dell até 3000 com 16GB de RAM e SSD")
    assert r2["executar_busca"] is True
    assert "criterios" in r2 and r2["criterios"] is not None
    assert "Entendi" in r2["resposta"]


def test_fallback():
    llm = MockLLM()
    cm = ConversationManager(llm=llm)
    _ = cm.iniciar_conversa("u1", "Hugo")
    r = cm.processar_mensagem("u1", "Olá mundo")
    assert "Não entendi" in r["resposta"] or "reformular" in r["resposta"].lower()
