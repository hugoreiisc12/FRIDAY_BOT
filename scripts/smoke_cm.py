import os
import sys
# ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.config import ConversationManager

cm = ConversationManager()
print("LLM->", type(cm.llm).__name__)
print("START->", cm.iniciar_conversa("12345","Tester")[:120])
print("CHOICE->", cm.processar_mensagem("12345","1")["resposta"][:120])
print("SEARCH->", cm.processar_mensagem("12345","Notebook Dell até R$ 3000")["resposta"][:300])
