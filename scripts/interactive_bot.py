"""Simple interactive terminal to chat with ConversationManager"""
import sys
import os
# ensure project root is on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.config import ConversationManager


def run():
    cm = ConversationManager()
    uid = "terminal_user"
    print(cm.iniciar_conversa(uid, "Terminal"))
    print("Dicas: use /cart para ver carrinho, /checkout para finalizar manualmente, /reset para reiniciar a sessão, 'sair' para encerrar.")

    try:
        while True:
            msg = input("Você: ")
            cmd = msg.strip().lower()
            if cmd in ("sair", "quit", "exit"):
                print("Encerrando.")
                break
            if cmd == "/cart":
                ctx = cm.obter_contexto(uid)
                carrinho = ctx.carrinho if ctx else []
                if not carrinho:
                    print("Bot: Seu carrinho está vazio.")
                else:
                    print("Bot: Itens no carrinho:")
                    for i, p in enumerate(carrinho, start=1):
                        print(f"  {i}) {p.get('nome')} — R$ {p.get('preco')}")
                continue
            if cmd == "/checkout":
                res = cm.processar_mensagem(uid, "4")
                print("Bot:", res.get("resposta"))
                res2 = cm.processar_mensagem(uid, "Quero finalizar a compra")
                print("Bot:", res2.get("resposta"))
                if res2.get("manual_checkout"):
                    print("Bot: Para finalizar, siga as instruções manuais fornecidas.")
                continue
            if cmd == "/reset":
                cm.resetar(uid)
                print("Bot: Sessão reiniciada.")
                print(cm.iniciar_conversa(uid, "Terminal"))
                continue

            # default: forward to ConversationManager
            res = cm.processar_mensagem(uid, msg)
            print("Bot:", res.get("resposta"))
            # helper: if executor hint returned
            if res.get("executar_busca"):
                print("[Executor] executar_busca=True -> criterios:", res.get("criterios"))
            # if hits returned show them
            if res.get("hits"):
                print("Bot: Produtos encontrados (use o número para selecionar):")
                for i, h in enumerate(res.get("hits"), start=1):
                    print(f"  {i}) {h.get('nome')} — R$ {h.get('preco')} — {h.get('loja')}")
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário")


if __name__ == '__main__':
    run()
