"""Demo automático: busca -> seleciona -> adiciona ao carrinho -> finaliza (manual)

Roda um fluxo previsível usando o Mock RAG definido em `tests/test_flow_purchase.MockRAGForFlow`.
"""
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.config import ConversationManager
from tests.test_flow_purchase import MockRAGForFlow


def run_demo():
    cm = ConversationManager(llm=None)
    cm.rag = MockRAGForFlow()
    uid = "demo_user"

    print("--- Iniciando demo automático do fluxo de compra ---")
    print("1) Iniciar conversa")
    intro = cm.iniciar_conversa(uid, "DemoUser")
    print(intro)

    print("\n2) Escolher modo BUSCAR (1)")
    r1 = cm.processar_mensagem(uid, "1")
    print(r1)

    print("\n3) Enviar busca detalhada")
    r2 = cm.processar_mensagem(uid, "Quero notebook Dell até R$3000 com 16GB RAM e SSD")
    print(r2)

    print("\n4) Selecionar produto 2")
    r3 = cm.processar_mensagem(uid, "2")
    print(r3)

    print("\n5) Confirmar adição ao carrinho (sim)")
    r4 = cm.processar_mensagem(uid, "sim")
    print(r4)

    print("\n6) Ir para finalizar (4)")
    r5 = cm.processar_mensagem(uid, "4")
    print(r5)

    print("\n7) Solicitar finalizar a compra")
    r6 = cm.processar_mensagem(uid, "Quero finalizar a compra")
    print(r6)

    print("\n--- Demo finalizado ---")


if __name__ == '__main__':
    run_demo()
