"""Entry point demo for local development."""
from ai.conversation_manager import ConversationManager


class MockLLM:
    def generate(self, prompt):
        return {"resposta": "Olá! Posso ajudar.", "executar_busca": False}


def main():
    cm = ConversationManager(MockLLM())
    print(cm.iniciar_conversa("demo_user", "Dev"))
    resp = cm.processar_mensagem("demo_user", "Quero notebook Dell até 3000")
    print(resp)


if __name__ == '__main__':
    main()
