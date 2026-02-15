from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class EstadoBot(Enum):
    INICIAL = "INICIAL"
    AGUARDANDO_ESCOLHA = "AGUARDANDO_ESCOLHA"
    MODO_BUSCAR = "MODO_BUSCAR"
    MODO_COMPARAR = "MODO_COMPARAR"
    MODO_NEGOCIAR = "MODO_NEGOCIAR"
    MODO_FINALIZAR = "MODO_FINALIZAR"


class ModoAcao(Enum):
    BUSCAR_PRODUTOS = "BUSCAR_PRODUTOS"
    COMPARAR_OPCOES = "COMPARAR_OPCOES"
    NEGOCIAR_PRECOS = "NEGOCIAR_PRECOS"
    FINALIZAR_COMPRA = "FINALIZAR_COMPRA"


@dataclass
class ContextoConversa:
    user_id: str
    nome_usuario: Optional[str] = None
    estado: EstadoBot = EstadoBot.INICIAL
    modo_acao: Optional[ModoAcao] = None
    preferencias: Dict[str, Any] = field(default_factory=dict)
    produtos: List[Dict] = field(default_factory=list)
    mensagens: List[Dict] = field(default_factory=list)


class ConversationManager:
    """Gerencia contextos por user_id e roteia mensagens para modos.

    A implementação abaixo é mínima; o LLM deve ser injetado e possuir um
    método `generate(prompt: str) -> str` (mock fácil para testes).
    """

    def __init__(self, llm):
        self.contextos: Dict[str, ContextoConversa] = {}
        self.llm = llm

    def iniciar_conversa(self, user_id: str, nome: Optional[str] = None) -> str:
        ctx = ContextoConversa(user_id=user_id, nome_usuario=nome)
        self.contextos[user_id] = ctx
        return f"Olá {nome or 'usuário'}! Em que posso ajudar hoje?"

    def _get_ctx(self, user_id: str) -> ContextoConversa:
        if user_id not in self.contextos:
            self.contextos[user_id] = ContextoConversa(user_id=user_id)
        return self.contextos[user_id]

    def processar_mensagem(self, user_id: str, mensagem: str) -> Dict[str, Any]:
        ctx = self._get_ctx(user_id)
        ctx.mensagens.append({"in": mensagem})

        # Simples detecção de intenção baseada em palavras-chave (placeholder)
        lower = mensagem.lower()
        # Support selecting modes via number or keywords (1..4)
        tokens = __import__('re').findall(r"\b\w+\b", lower)
        if '1' in tokens or any(x in lower for x in ['buscar', 'busca', 'procurar']):
            ctx.estado = EstadoBot.MODO_BUSCAR
            ctx.modo_acao = ModoAcao.BUSCAR_PRODUTOS
            resposta = "✅ Modo: **BUSCAR PRODUTOS** 🔍\n\nO que você procura?\n\n💡 Exemplo:\n\"Notebook Dell até R$ 3000\"\n\nMe conte! 👇"
            ctx.mensagens.append({"out": resposta})
            return {"resposta": resposta, "estado": ctx.estado.value, "modo": ctx.modo_acao.value}

        if '2' in tokens or any(x in lower for x in ['comparar', 'compara']):
            ctx.estado = EstadoBot.MODO_COMPARAR
            ctx.modo_acao = ModoAcao.COMPARAR_OPCOES
            resposta = "✅ Modo: **COMPARAR OPÇÕES** 📊\n\nO que quer comparar?\n\n💡 Exemplo:\n\"iPhone 13 vs Samsung S21\"\n\nMe diga! 👇"
            ctx.mensagens.append({"out": resposta})
            return {"resposta": resposta, "estado": ctx.estado.value, "modo": ctx.modo_acao.value}

        if '3' in tokens or any(x in lower for x in ['negociar', 'negocia', 'desconto', 'preço']):
            ctx.estado = EstadoBot.MODO_NEGOCIAR
            ctx.modo_acao = ModoAcao.NEGOCIAR_PRECOS
            resposta = "✅ Modo: **NEGOCIAR PREÇOS** 💰\n\nQual produto quer negociar?\n\n💡 Exemplo:\n\"PlayStation 5\"\n\nQual é? 👇"
            ctx.mensagens.append({"out": resposta})
            return {"resposta": resposta, "estado": ctx.estado.value, "modo": ctx.modo_acao.value}

        if '4' in tokens or any(x in lower for x in ['finalizar', 'comprar', 'checkout']):
            ctx.estado = EstadoBot.MODO_FINALIZAR
            ctx.modo_acao = ModoAcao.FINALIZAR_COMPRA
            resposta = "✅ Modo: **FINALIZAR COMPRA** ✅\n\nQual produto vai comprar?\n\n💡 Se já escolheu:\nMe diga qual\n\n💡 Se não escolheu:\nPosso te ajudar a buscar!\n\nComo prefere? 👇"
            ctx.mensagens.append({"out": resposta})
            return {"resposta": resposta, "estado": ctx.estado.value, "modo": ctx.modo_acao.value}
        if any(w in lower for w in ["quero", "procuro", "buscar", "encontre"]):
            ctx.estado = EstadoBot.MODO_BUSCAR
            ctx.modo_acao = ModoAcao.BUSCAR_PRODUTOS
            # delegate to LLM (mockable) - prefer callable interface (messages) if available
            prompt = f"Você é um especialista em buscar produtos. Criteria: {mensagem}"
            llm_output = None
            resposta = ""
            executar_busca = True
            criterios = {"query": mensagem}

            try:
                if callable(self.llm):
                    # create minimal message-like objects
                    Sys = type('Sys', (), {'content': prompt})
                    Hum = type('Hum', (), {'content': mensagem})
                    llm_output = self.llm([Sys(), Hum()])
                    # If returns object with content
                    if hasattr(llm_output, 'content'):
                        resposta = llm_output.content
                    elif isinstance(llm_output, dict):
                        resposta = llm_output.get('resposta', '')
                        executar_busca = llm_output.get('executar_busca', True)
                        criterios = llm_output.get('criterios', criterios)
                    else:
                        resposta = str(llm_output)
                else:
                    llm_output = self.llm.generate(prompt)
                    if isinstance(llm_output, dict):
                        resposta = llm_output.get('resposta', '')
                        executar_busca = llm_output.get('executar_busca', True)
                        criterios = llm_output.get('criterios', criterios)
                    else:
                        resposta = str(llm_output)
            except Exception as e:
                # fallback
                resposta = str(llm_output or e)

            ctx.mensagens.append({"out": resposta})
            return {"resposta": resposta, "executar_busca": executar_busca, "criterios": criterios}

        # fallback: echo
        ctx.mensagens.append({"out": "Desculpe, não entendi. Pode reformular?"})
        return {"resposta": "Desculpe, não entendi. Pode reformular?"}
    # Métodos de modo (stubs para evolução)
    def _modo_buscar(self, ctx: ContextoConversa, mensagem: str) -> Dict:
        raise NotImplementedError

    def _modo_comparar(self, ctx: ContextoConversa, mensagem: str) -> Dict:
        raise NotImplementedError

    def _modo_negociar(self, ctx: ContextoConversa, mensagem: str) -> Dict:
        raise NotImplementedError

    def _modo_finalizar(self, ctx: ContextoConversa, mensagem: str) -> Dict:
        raise NotImplementedError
