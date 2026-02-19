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


def test_uses_langchain_chatopenai_with_hf_token(monkeypatch):
    import sys, types

    # Dummy ChatOpenAI replacement
    class DummyChat:
        def __init__(self, *args, **kwargs):
            pass
        def __call__(self, messages):
            return type('R', (), {'content': 'resposta dummy'})

    # Ensure the function will import our dummy module
    monkeypatch.setenv('HF_TOKEN', 'hf_test_token')
    monkeypatch.setenv('LLM_PROVIDER', 'hf')
    monkeypatch.setitem(sys.modules, 'langchain_openai', types.SimpleNamespace(ChatOpenAI=DummyChat))
    monkeypatch.setitem(sys.modules, 'langchain.chat_models', types.SimpleNamespace(ChatOpenAI=DummyChat))

    # Initialize without passing llm — should pick up DummyChat via HF_TOKEN
    cm = ConversationManager()
    assert hasattr(cm, 'llm') and isinstance(cm.llm, DummyChat)
    # verify it responds using dummy
    _ = cm.iniciar_conversa('u_hf', 'Tester')
    out = cm.processar_mensagem('u_hf', '1')
    assert 'BUSCAR PRODUTOS' in out['resposta']
