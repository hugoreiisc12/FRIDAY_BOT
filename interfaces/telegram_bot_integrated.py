# Minimal integrated Telegram handler example (mockable for tests)
import asyncio
from ai.conversation_manager import ConversationManager


class MockTelegramUpdate:
    def __init__(self, user_id, text):
        self.message = type("M", (), {"text": text, "chat": type("C", (), {"id": user_id})})


async def handle_message(cm: ConversationManager, update: MockTelegramUpdate):
    user_id = str(update.message.chat.id)
    mensagem = update.message.text
    resultado = cm.processar_mensagem(user_id, mensagem)
    # In real bot: await update.message.reply_text(resultado['resposta'])
    return resultado


def main():
    # Example usage with MockLLM
    class MockLLM:
        def generate(self, prompt):
            return {"resposta": "OK", "executar_busca": False}

    cm = ConversationManager(MockLLM())
    print(cm.iniciar_conversa("user1", "Hugo"))

if __name__ == '__main__':
    main()
