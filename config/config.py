#!/usr/bin/env python3
"""
SEXTA FEIRA - Gerenciador de Conversação Inteligente
Sistema de estados com prompts especializados por ação escolhida
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import os
import re

# New states for selection and confirmation

# Optional langchain imports (support running without langchain installed)
try:
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import SystemMessage, HumanMessage
    LANGCHAIN_AVAILABLE = True
except Exception:
    ChatOpenAI = None
    LANGCHAIN_AVAILABLE = False

    class SystemMessage:
        def __init__(self, content: str = ""):
            self.content = content

    class HumanMessage:
        def __init__(self, content: str = ""):
            self.content = content


# ============================================================================
# ESTADOS E TIPOS
# ============================================================================

class EstadoBot(Enum):
    """Estados possíveis do bot"""
    INICIAL = "inicial"
    AGUARDANDO_ESCOLHA = "aguardando_escolha"
    MODO_BUSCAR = "modo_buscar"
    AGUARDANDO_SELECAO_PRODUTO = "aguardando_selecao_produto"
    AGUARDANDO_CONFIRMACAO_ADICAO = "aguardando_confirmacao_adicao"
    MODO_COMPARAR = "modo_comparar"
    MODO_NEGOCIAR = "modo_negociar"
    MODO_FINALIZAR = "modo_finalizar"


class ModoAcao(Enum):
    """Modos de ação do bot"""
    BUSCAR_PRODUTOS = "buscar"
    COMPARAR_OPCOES = "comparar"
    NEGOCIAR_PRECOS = "negociar"
    FINALIZAR_COMPRA = "finalizar"


# ============================================================================
# PROMPTS ESPECIALIZADOS POR MODO
# ============================================================================

PROMPTS = {
    "buscar": """Você é um ESPECIALISTA EM BUSCA DE PRODUTOS eficiente e organizado.

OBJETIVO: Entender exatamente o que o cliente quer e buscar os melhores produtos.

COMPORTAMENTO:
- Faça perguntas específicas (máximo 2-3 por vez)
- Confirme marca, orçamento e especificações
- Seja ATENTO: se o cliente muda de ideia, adapte-se
- Após coletar informações, confirme antes de buscar

SEMPRE conduza para a compra ao final.

TOM: Profissional, prestativo, eficiente

Histórico recente:
{historico}

RESPONDA de forma natural:""",

    "comparar": """Você é um ANALISTA ESPECIALISTA EM COMPARAÇÃO de produtos.

OBJETIVO: Comparar produtos de forma objetiva e recomendar o melhor.

COMPORTAMENTO:
- Compare preço total (produto + frete)
- Liste vantagens e desvantagens
- Seja imparcial mas faça uma recomendação clara
- Sempre pergunte qual o cliente prefere

FORMATO:
📊 COMPARAÇÃO:
🔵 OPÇÃO 1: [produto] - R$ XXX
✅ Vantagens: [lista]
⚠️ Atenção: [lista]

🟢 OPÇÃO 2: [produto] - R$ XXX
✅ Vantagens: [lista]
⚠️ Atenção: [lista]

🎯 RECOMENDAÇÃO: [qual e por quê]

Qual faz mais sentido pra você?

TOM: Consultivo, analítico, confiável

Histórico:
{historico}

RESPONDA comparando:""",

    "negociar": """Você é um NEGOCIADOR ESTRATÉGICO focado em conseguir o melhor preço.

OBJETIVO: Encontrar TODAS as formas de economizar.

ESTRATÉGIAS:
1. Comparar lojas diferentes
2. Buscar cupons/promoções
3. Sugerir combos
4. Indicar cashback
5. Alertar sobre frete grátis

COMPORTAMENTO:
- Mostre economia em R$
- Celebre cada economia: "Olha só, R$ 300 de desconto!"
- Crie urgência (sem mentir)
- Sempre pergunte: "Fecha por esse preço?"

FORMATO:
💰 ECONOMIA ENCONTRADA:

Preço original: R$ XXX
✅ Loja Y: -R$ XXX
✅ Cupom: -R$ XXX
✅ Cashback: +R$ XXX

💎 TOTAL: R$ XXX (economia de R$ XXX!)

Fecha agora?

TOM: Entusiasta, estratégico, parceiro

Histórico:
{historico}

RESPONDA com estratégias:""",

    "finalizar": """Você é um ASSISTENTE DE CHECKOUT que guia o cliente passo a passo.

OBJETIVO: Preparar o cliente para finalizar a compra de forma clara e segura.

COMPORTAMENTO:
- Explique cada passo do resumo da compra
- Tranquilize o cliente ("100% seguro")
- Informe que o pagamento será realizado externamente (manual) se o gateway estiver desabilitado
- Nunca pressione

FORMATO:
📋 RESUMO:
🛒 Produto: [nome]
💰 Total: R$ XXX,XX
📦 Entrega: X dias

🔗 FINALIZAÇÃO (MANUAL):
- No momento, os pagamentos são encaminhados manualmente. Informe ao cliente como proceder:
  1) Acesse a página do produto/loja
  2) Escolha a forma de pagamento preferida (PIX, Cartão ou Boleto)
  3) Siga as instruções do vendedor para concluir a compra

Se quiser, posso gerar um resumo da compra com os dados e instruções para você encaminhar ao checkout.

TOM: Confiável, tranquilizador

Histórico:
{historico}

RESPONDA guiando (ofereça resumo se solicitado):"""
}


# ============================================================================
# CONTEXTO DE CONVERSA
# ============================================================================

@dataclass
class ContextoConversa:
    """Contexto da conversa"""
    
    user_id: str
    nome_usuario: str = "Cliente"
    
    estado: EstadoBot = EstadoBot.INICIAL
    modo_acao: Optional[ModoAcao] = None
    
    # Dados
    produto_buscado: str = ""
    orcamento_max: Optional[float] = None
    marca: str = ""
    
    produtos: List[Dict] = field(default_factory=list)
    produto_selecionado: Optional[Dict] = None
    carrinho: List[Dict] = field(default_factory=list)
    
    mensagens: List[Dict] = field(default_factory=list)
    criado_em: datetime = field(default_factory=datetime.now)
    
    def adicionar_mensagem(self, role: str, conteudo: str):
        self.mensagens.append({
            "role": role,
            "content": conteudo,
            "time": datetime.now().isoformat()
        })
    
    def historico_formatado(self, ultimas: int = 4) -> str:
        if not self.mensagens:
            return "Início da conversa"
        
        h = []
        for msg in self.mensagens[-ultimas:]:
            role = "Você" if msg["role"] == "assistant" else "Cliente"
            h.append(f"{role}: {msg['content'][:100]}")
        return "\n".join(h)


# ============================================================================
# GERENCIADOR
# ============================================================================

class ConversationManager:
    """Gerenciador de conversação com estados"""
    
    def __init__(self, openai_api_key: Optional[str] = None, llm: Optional[Any] = None):
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # Prefer explicit LLM injection (tests / LangChain). If not provided, try to
        # create a ChatOpenAI (langchain). If langchain not available or no key,
        # fallback to a built-in MockLLM for predictable behavior in tests.
        if llm is not None:
            self.llm = llm
        elif api_key:
            # Prefer using OpenAILangChainService wrapper when available
            try:
                from core.services_langchain import OpenAILangChainService
                try:
                    self.llm = OpenAILangChainService(api_key=api_key)
                    print("✅ OpenAILangChainService inicializado")
                except Exception as e:
                    print(f"⚠️ Falha ao inicializar OpenAILangChainService: {e}")
                    # fallback to ChatOpenAI if available, otherwise try direct OpenAI wrapper
                    if ChatOpenAI is not None:
                        try:
                            self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0.7, max_tokens=250)
                            print("✅ ChatOpenAI inicializado como fallback")
                        except Exception as e2:
                            print(f"⚠️ Falha ao inicializar ChatOpenAI: {e2}")
                            # try direct openai wrapper
                            try:
                                from core.services_openai import OpenAISimpleService
                                self.llm = OpenAISimpleService(api_key=api_key)
                                print("✅ OpenAISimpleService inicializado como fallback")
                            except Exception as e3:
                                print(f"⚠️ Falha ao inicializar OpenAISimpleService: {e3}")
                                self.llm = None
                    else:
                        try:
                            from core.services_openai import OpenAISimpleService
                            self.llm = OpenAISimpleService(api_key=api_key)
                            print("✅ OpenAISimpleService inicializado")
                        except Exception as e4:
                            print(f"⚠️ Falha ao inicializar OpenAISimpleService: {e4}")
                            self.llm = None
            except Exception:
                # OpenAILangChainService not available; try ChatOpenAI directly or a simple OpenAI wrapper
                if ChatOpenAI is not None:
                    try:
                        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0.7, max_tokens=250)
                        print("✅ ChatOpenAI inicializado")
                    except Exception as e:
                        print(f"⚠️ Falha ao inicializar ChatOpenAI: {e}")
                        # try direct openai wrapper
                        try:
                            from core.services_openai import OpenAISimpleService
                            self.llm = OpenAISimpleService(api_key=api_key)
                            print("✅ OpenAISimpleService inicializado como fallback")
                        except Exception as e2:
                            print(f"⚠️ Falha ao inicializar OpenAISimpleService: {e2}")
                            self.llm = None
                else:
                    # try direct openai wrapper
                    try:
                        from core.services_openai import OpenAISimpleService
                        self.llm = OpenAISimpleService(api_key=api_key)
                        print("✅ OpenAISimpleService inicializado")
                    except Exception as e:
                        print(f"⚠️ OpenAI configurada mas não foi possível utilizar (langchain/chatopenai/openai): {e}")
                        # try hf if provider suggests or hf token exists
                        hf_pref = os.getenv('LLM_PROVIDER','').lower() == 'hf'
                        hf_token = os.getenv('HF_API_TOKEN')
                        if hf_pref or hf_token:
                            # Prefer hf router service if provider set to hf-router or HF_TOKEN present
                            hf_router_pref = os.getenv('LLM_PROVIDER','').lower() == 'hf-router'
                            hf_token = os.getenv('HF_TOKEN') or hf_token
                            try:
                                if hf_router_pref or os.getenv('HF_TOKEN'):
                                    from core.services_hf_router import HuggingFaceRouterService
                                    self.llm = HuggingFaceRouterService(api_token=hf_token)
                                    print("✅ HuggingFaceRouterService inicializado como fallback")
                                else:
                                    from core.services_hf import HuggingFaceService
                                    self.llm = HuggingFaceService(api_token=hf_token)
                                    print("✅ HuggingFaceService inicializado como fallback")
                            except Exception as e3:
                                print(f"⚠️ Falha ao inicializar serviço HF: {e3}")
                                print("ℹ️ Usando MockLLM")
                                try:
                                    from ai.mock_llm import MockLLM
                                    self.llm = MockLLM()
                                except Exception as e4:
                                    print(f"⚠️ MockLLM não disponível: {e4}")
                                    self.llm = None
                        else:
                            print("ℹ️ Usando MockLLM")
                            try:
                                from ai.mock_llm import MockLLM
                                self.llm = MockLLM()
                            except Exception as e2:
                                print(f"⚠️ MockLLM não disponível: {e2}")
                                self.llm = None
        else:
            # No OPENAI key — respect LLM_PROVIDER or available provider tokens (HF / Gemini)
            hf_pref = os.getenv('LLM_PROVIDER','').lower() in ('hf', 'hf-router')
            hf_token = os.getenv('HF_TOKEN') or os.getenv('HF_API_TOKEN')
            gem_key = os.getenv('GEMINI_API_KEY')

            if hf_pref or hf_token:
                try:
                    if os.getenv('LLM_PROVIDER','').lower() == 'hf-router' or os.getenv('HF_TOKEN'):
                        from core.services_hf_router import HuggingFaceRouterService
                        self.llm = HuggingFaceRouterService(api_token=hf_token)
                        print("✅ HuggingFaceRouterService inicializado (sem OPENAI_API_KEY)")
                    else:
                        from core.services_hf import HuggingFaceService
                        self.llm = HuggingFaceService(api_token=hf_token)
                        print("✅ HuggingFaceService inicializado (sem OPENAI_API_KEY)")
                except Exception as e:
                    print(f"⚠️ Falha ao inicializar serviço HF (sem OPENAI): {e}")
                    self.llm = None
            elif gem_key:
                try:
                    from core.services_gemini import GeminiService
                    self.llm = GeminiService(api_key=gem_key)
                    print("✅ GeminiService inicializado (sem OPENAI_API_KEY)")
                except Exception as e:
                    print(f"⚠️ Falha ao inicializar Gemini (sem OPENAI): {e}")
                    self.llm = None
            else:
                # fallback mock
                try:
                    from ai.mock_llm import MockLLM
                    self.llm = MockLLM()
                    print("ℹ️ Usando MockLLM (sem OPENAI_API_KEY)")
                except Exception as e:
                    print(f"⚠️ MockLLM não disponível: {e}")
                    self.llm = None

        self.contextos: Dict[str, ContextoConversa] = {}

        # RAG support (optional): try to create manager if available
        try:
            from ai.vector_db import EmbeddingService, VectorDBManager
            from ai.rag import RAGProductChain
            # initialize embedding & vector manager only if sentence-transformers + faiss available
            # user can override by passing rag_service to constructor in the future
            self.embedding_service = EmbeddingService()
            self.vector_manager = VectorDBManager(self.embedding_service)
            self.rag = RAGProductChain(self, self.vector_manager)  # placeholder; will be replaced with proper LLM wrapper
            # Note: we set rag to None if vector DB is not functional during runtime
        except Exception:
            self.embedding_service = None
            self.vector_manager = None
            self.rag = None

        # Optional: Gemini search LLM (prefer for product searches)
        self.gemini = None
        try:
            gem_key = os.getenv('GEMINI_API_KEY')
            gem_pref = os.getenv('SEARCH_LLM_PROVIDER','').lower() == 'gemini'
            if gem_key or gem_pref:
                from core.services_gemini import GeminiService
                self.gemini = GeminiService(api_key=gem_key)
                print('✅ GeminiService inicializado para buscas')
        except Exception as e:
            print(f"⚠️ Falha ao inicializar GeminiService: {e}")

        # Payments: feature flag to allow disabling gateway integration
        self.payments_enabled = os.getenv("PAYMENTS_ENABLED", "false").lower() == "true"

        # Optional: Supabase conversation store (if configured)
        self.store = None
        try:
            if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
                from core.supabase_store import SupabaseConversationStore
                self.store = SupabaseConversationStore(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
                print("✅ SupabaseConversationStore inicializado")
        except Exception as e:
            print(f"⚠️ Falha ao inicializar SupabaseConversationStore: {e}")

        print("✅ ConversationManager pronto")
    
    def iniciar_conversa(self, user_id: str, nome: str = "Cliente") -> str:
        """Inicia conversa com apresentação"""
        
        ctx = ContextoConversa(user_id=user_id, nome_usuario=nome)
        self.contextos[user_id] = ctx
        
        msg = f"""Olá {nome}! 👋

Sou o **SEXTA FEIRA**, seu assistente de compras! 🛒

Posso te ajudar de 4 formas:

1️⃣ **Buscar Produtos** 🔍
   Encontro o que você procura

2️⃣ **Comparar Opções** 📊
   Analiso lado a lado

3️⃣ **Negociar Preços** 💰
   Busco os melhores descontos

4️⃣ **Finalizar Compra** ✅
   Guio no checkout seguro

**Qual opção?** Digite o número!"""
        
        ctx.adicionar_mensagem("assistant", msg)
        ctx.estado = EstadoBot.AGUARDANDO_ESCOLHA

        # Persist initial session & message if store available
        if self.store:
            try:
                self.store.create_session(ctx)
                # save any unsaved messages (e.g., the assistant's greeting)
                self._persist_unsaved_messages(ctx)
            except Exception as e:
                print(f"⚠️ Falha ao criar sessão no Supabase: {e}")
        
        return msg
    
    def processar_mensagem(self, user_id: str, mensagem: str) -> Dict[str, Any]:
        """Processa mensagem"""
        
        if user_id not in self.contextos:
            resp = self.iniciar_conversa(user_id)
            return {"resposta": resp, "estado": "aguardando_escolha"}
        
        ctx = self.contextos[user_id]
        ctx.adicionar_mensagem("user", mensagem)

        # persist user message immediately if store available
        if self.store:
            try:
                self._persist_unsaved_messages(ctx)
            except Exception as e:
                print(f"⚠️ Falha ao salvar mensagem de usuário: {e}")
        
        if ctx.estado == EstadoBot.AGUARDANDO_ESCOLHA:
            res = self._escolher_modo(ctx, mensagem)
        elif ctx.estado == EstadoBot.MODO_BUSCAR:
            res = self._modo_buscar(ctx, mensagem)
        elif ctx.estado == EstadoBot.AGUARDANDO_SELECAO_PRODUTO:
            res = self._processar_selecao_produto(ctx, mensagem)
        elif ctx.estado == EstadoBot.AGUARDANDO_CONFIRMACAO_ADICAO:
            res = self._processar_confirmacao_adicao(ctx, mensagem)
        elif ctx.estado == EstadoBot.MODO_COMPARAR:
            res = self._modo_comparar(ctx, mensagem)
        elif ctx.estado == EstadoBot.MODO_NEGOCIAR:
            res = self._modo_negociar(ctx, mensagem)
        elif ctx.estado == EstadoBot.MODO_FINALIZAR:
            res = self._modo_finalizar(ctx, mensagem)
        else:
            res = {"resposta": "Erro. Digite /start", "estado": "erro"}
        
        # Persist any assistant messages generated during handling
        if self.store:
            try:
                self._persist_unsaved_messages(ctx)
            except Exception as e:
                print(f"⚠️ Falha ao salvar mensagens no Supabase: {e}")
        
        return res
    
    def _escolher_modo(self, ctx: ContextoConversa, msg: str) -> Dict:
        """Processa escolha do modo"""
        
        m = msg.lower()
        
        if any(x in m for x in ["1", "buscar", "busca", "procurar"]):
            ctx.modo_acao = ModoAcao.BUSCAR_PRODUTOS
            ctx.estado = EstadoBot.MODO_BUSCAR
            
            resp = """✅ Modo: **BUSCAR PRODUTOS** 🔍

O que você procura?

💡 Exemplo:
"Notebook Dell até R$ 3000"

Me conte! 👇"""
            
        elif any(x in m for x in ["2", "comparar", "compara"]):
            ctx.modo_acao = ModoAcao.COMPARAR_OPCOES
            ctx.estado = EstadoBot.MODO_COMPARAR
            
            resp = """✅ Modo: **COMPARAR OPÇÕES** 📊

O que quer comparar?

💡 Exemplo:
"iPhone 13 vs Samsung S21"

Me diga! 👇"""
            
        elif any(x in m for x in ["3", "negociar", "negocia", "desconto", "preço"]):
            ctx.modo_acao = ModoAcao.NEGOCIAR_PRECOS
            ctx.estado = EstadoBot.MODO_NEGOCIAR
            
            resp = """✅ Modo: **NEGOCIAR PREÇOS** 💰

Qual produto quer negociar?

💡 Exemplo:
"PlayStation 5"

Qual é? 👇"""
            
        elif any(x in m for x in ["4", "finalizar", "comprar", "checkout"]):
            ctx.modo_acao = ModoAcao.FINALIZAR_COMPRA
            ctx.estado = EstadoBot.MODO_FINALIZAR
            
            resp = """✅ Modo: **FINALIZAR COMPRA** ✅

Qual produto vai comprar?

💡 Se já escolheu:
Me diga qual

💡 Se não escolheu:
Posso te ajudar a buscar!

Como prefere? 👇"""
            
        else:
            resp = """Não entendi 😅

Digite:
1️⃣ Buscar
2️⃣ Comparar
3️⃣ Negociar
4️⃣ Finalizar"""
            
            ctx.adicionar_mensagem("assistant", resp)
            return {"resposta": resp, "estado": "aguardando_escolha"}
        
        ctx.adicionar_mensagem("assistant", resp)
        return {
            "resposta": resp,
            "estado": ctx.estado.value,
            "modo": ctx.modo_acao.value
        }
    
    def _modo_buscar(self, ctx: ContextoConversa, msg: str) -> Dict:
        """Modo buscar produtos"""

        deve_buscar = self._check_buscar(msg)
        criterios = self._extrair_criterios(msg) if deve_buscar else None

        # 1) Use RAG if available
        if deve_buscar and self.rag is not None:
            try:
                rag_out = self.rag.retrieve_and_generate(msg, k=5)
                hits = rag_out.get("hits", [])
                resposta_rag = rag_out.get("resposta")
                # Save products in context
                ctx.produtos = hits
                # If RAG provided a direct recommendation text, use it; otherwise list products
                if resposta_rag:
                    # If RAG returned also hits, append the numbered list to help selection
                    if hits:
                        lista = self._format_lista_produtos(hits)
                        resp = resposta_rag + "\n\n" + lista + "\n\nDigite o número do produto para ver as especificações ou digite 'refinar'."
                    else:
                        resp = resposta_rag
                else:
                    lista = self._format_lista_produtos(hits)
                    resp = f"✅ Encontrei {len(hits)} produtos:\n" + lista + "\n\nDigite o número do produto para ver as especificações ou digite 'refinar'."

                ctx.adicionar_mensagem("assistant", resp)
                ctx.estado = EstadoBot.AGUARDANDO_SELECAO_PRODUTO
                return {"resposta": resp, "estado": ctx.estado.value, "executar_busca": True, "hits": hits}
            except Exception as e:
                print(f"⚠️ Erro ao executar RAG: {e}")

        # 2) prefer Gemini for search if available
        if self.gemini is not None:
            try:
                prompt = PROMPTS['buscar'].replace("{historico}", ctx.historico_formatado()) + "\n\nQuery: " + msg
                resp = self.gemini.generate(prompt)
                ctx.adicionar_mensagem("assistant", resp)
                # do not trigger external product search if Gemini provided direct answer; still allow execute flag
                return {"resposta": resp, "estado": "buscar", "executar_busca": deve_buscar, "criterios": criterios}
            except Exception as e:
                print(f"⚠️ Falha ao usar Gemini para busca: {e}")

        # 3) fallback LLM (existing behavior)
        resp = self._gerar_llm("buscar", ctx, msg)
        ctx.adicionar_mensagem("assistant", resp)
        return {"resposta": resp, "estado": "buscar", "executar_busca": deve_buscar, "criterios": criterios}
    
    def _modo_comparar(self, ctx: ContextoConversa, msg: str) -> Dict:
        resp = self._gerar_llm("comparar", ctx, msg)
        ctx.adicionar_mensagem("assistant", resp)
        return {"resposta": resp, "estado": "comparar"}

    # --- Helpers for selection & cart flow
    def _format_lista_produtos(self, produtos: List[Dict]) -> str:
        if not produtos:
            return "Nenhum produto encontrado." 
        linhas = []
        for i, p in enumerate(produtos, start=1):
            nome = p.get("nome") or p.get("title") or "Sem nome"
            preco = p.get("preco") or p.get("price") or "n/a"
            loja = p.get("loja") or p.get("store") or "-"
            linhas.append(f"{i}) {nome} — R$ {preco} — {loja}")
        return "\n".join(linhas)

    def _processar_selecao_produto(self, ctx: ContextoConversa, msg: str) -> Dict:
        """Processa a seleção de um produto por número"""
        m = msg.strip().lower()
        if m in ("refinar", "refinar busca"):
            ctx.estado = EstadoBot.MODO_BUSCAR
            resp = "Certo — me diga como quer refinar a busca."
            ctx.adicionar_mensagem("assistant", resp)
            return {"resposta": resp, "estado": ctx.estado.value}

        # numeric selection
        try:
            idx = int(m) - 1
            if idx < 0 or idx >= len(ctx.produtos):
                raise ValueError
            produto = ctx.produtos[idx]
            ctx.produto_selecionado = produto
            # show specs
            spec = produto.get("specs") or produto.get("descricao") or "Sem especificações disponíveis."
            resp = f"🔎 *{produto.get('nome','Produto')}*\nPreço: R$ {produto.get('preco','n/a')}\nLoja: {produto.get('loja','-')}\n\nEspecificações:\n{spec}\n\nDeseja adicionar este produto ao carrinho? (sim/não)"
            ctx.adicionar_mensagem("assistant", resp)
            ctx.estado = EstadoBot.AGUARDANDO_CONFIRMACAO_ADICAO
            return {"resposta": resp, "estado": ctx.estado.value, "produto": produto}
        except ValueError:
            resp = "Número inválido. Digite o número do produto da lista ou 'refinar'."
            ctx.adicionar_mensagem("assistant", resp)
            return {"resposta": resp, "estado": ctx.estado.value}

    def _processar_confirmacao_adicao(self, ctx: ContextoConversa, msg: str) -> Dict:
        m = msg.strip().lower()
        if m in ("sim", "s", "ok", "confirmar"):
            produto = ctx.produto_selecionado
            if not produto:
                return {"resposta": "Nenhum produto selecionado.", "estado": ctx.estado.value}
            # add to cart
            ctx.carrinho.append(produto)
            resp = f"✅ Produto *{produto.get('nome')}* adicionado ao carrinho!\nTotal no carrinho: R$ {sum([p.get('preco',0) for p in ctx.carrinho])}\n\nDeseja continuar comprando ou finalizar? (digite 'continuar' ou 'finalizar')"
            ctx.adicionar_mensagem("assistant", resp)
            # set state back to main menu for choice
            ctx.estado = EstadoBot.AGUARDANDO_ESCOLHA
            return {"resposta": resp, "estado": ctx.estado.value, "carrinho": ctx.carrinho}
        else:
            resp = "Ok, não adicionei ao carrinho. Quer ver outro produto ou refinar a busca?"
            ctx.adicionar_mensagem("assistant", resp)
            ctx.estado = EstadoBot.AGUARDANDO_SELECAO_PRODUTO
            return {"resposta": resp, "estado": ctx.estado.value}
    
    def _modo_negociar(self, ctx: ContextoConversa, msg: str) -> Dict:
        resp = self._gerar_llm("negociar", ctx, msg)
        ctx.adicionar_mensagem("assistant", resp)
        return {"resposta": resp, "estado": "negociar"}
    
    def _modo_finalizar(self, ctx: ContextoConversa, msg: str) -> Dict:
        """Modo finalizar: se pagamentos estiverem desabilitados, oriente para checkout manual."""
        # If payments integration disabled, return manual instructions
        if not self.payments_enabled:
            resp = self._gerar_llm("finalizar", ctx, msg)
            ctx.adicionar_mensagem("assistant", resp)
            return {"resposta": resp, "estado": "finalizar", "manual_checkout": True}

        # Otherwise try to process with payment manager (not implemented here)
        resp = self._gerar_llm("finalizar", ctx, msg)
        ctx.adicionar_mensagem("assistant", resp)
        return {"resposta": resp, "state": "finalizar"}
    
    def _gerar_llm(self, modo: str, ctx: ContextoConversa, msg: str) -> str:
        """Gera resposta com LLM"""
        
        if not self.llm:
            return "Desculpe, problema técnico."
        
        try:
            prompt = PROMPTS[modo].replace("{historico}", ctx.historico_formatado())
            
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=msg)
            ]
            
            resp = self.llm(messages)
            return resp.content.strip()
        except Exception as e:
            print(f"❌ Erro LLM: {e}")
            return "Desculpe, tive um problema. Repete?"
    
    def _check_buscar(self, msg: str) -> bool:
        """Verifica se deve executar busca"""
        m = msg.lower()
        
        # Produtos conhecidos
        prods = ["notebook", "celular", "tv", "iphone", "samsung"]
        tem_prod = any(p in m for p in prods)
        
        # Confirmação
        confirma = any(x in m for x in ["sim", "busca", "procura", "mostra"])
        
        # Detalhado
        detalhado = len(msg.split()) > 8
        # also consider price mentions or technical terms (e.g., 'GB', 'SSD', 'R$') as detailed
        tem_detalhe_tecnico = any(x in m for x in ['gb', 'ssd', 'r$', 'rs', '$']) or bool(re.search(r"\d+gb|\d+g", m))

        return (tem_prod and (detalhado or tem_detalhe_tecnico)) or confirma

    def _extrair_criterios(self, msg: str) -> Dict:
        """Extrai critérios da mensagem do usuário (valor, marca, query)."""
        crit = {"query": msg}

        # Valor (R$ 3000, 3000, etc.)
        match = re.search(r"r?\$?\s*(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)", msg.lower())
        if match:
            val = match.group(1).replace(".", "").replace(",", ".")
            try:
                crit["orcamento_max"] = float(val)
            except Exception:
                pass

        # Marca
        marcas = ["dell", "hp", "samsung", "lg", "apple", "xiaomi"]
        for m in marcas:
            if m in msg.lower():
                crit["marca"] = m
                break

        return crit
    
    def obter_contexto(self, user_id: str) -> Optional[ContextoConversa]:
        return self.contextos.get(user_id)
    
    def resetar(self, user_id: str):
        if user_id in self.contextos:
            del self.contextos[user_id]

    def _persist_unsaved_messages(self, ctx: ContextoConversa):
        """Persiste mensagens não salvas para uma sessão usando SupabaseConversationStore."""
        if not self.store:
            return
        for m in ctx.mensagens:
            # 'saved' flag indicates already persisted
            if m.get('saved'):
                continue
            try:
                self.store.save_message(ctx, m.get('role', 'user'), m.get('content', ''))
                m['saved'] = True
            except Exception as e:
                print(f"⚠️ Falha ao salvar message no Supabase: {e}")
                # don't raise — keep running
