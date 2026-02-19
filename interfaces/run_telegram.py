#!/usr/bin/env python3
"""
SEXTA FEIRA - Telegram Bot CORRIGIDO
Usa ConversationManager com LLM configurado
"""

import os
import sys

# Adicionar projeto ao path (raiz do workspace)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Importar ConversationManager principal (config/config.py)
from config.config import ConversationManager

# Telegram
try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        filters,
        ContextTypes
    )
except ImportError:
    raise SystemExit(
        "❌ python-telegram-bot não instalado!\n"
        "   pip install python-telegram-bot"
    )

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise SystemExit(
        "❌ TELEGRAM_BOT_TOKEN não configurado!\n"
        "   Configure no .env"
    )

# Criar ConversationManager (cria LLM automaticamente)
print("🔧 Inicializando ConversationManager...")
cm = ConversationManager()

# ============================================================================
# COMANDOS
# ============================================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user_id = str(update.effective_chat.id)
    nome = update.effective_user.first_name or "Cliente"
    
    resposta = cm.iniciar_conversa(user_id, nome)
    await update.message.reply_text(resposta, parse_mode="Markdown")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    msg = """📚 **AJUDA - SEXTA FEIRA BOT**

**Comandos:**
/start - Iniciar conversa
/help - Esta ajuda
/reset - Reiniciar conversa

**Como usar:**
1. /start para começar
2. Escolha uma opção (1-4)
3. Converse naturalmente!

**Dúvidas?** Digite sua pergunta!"""
    
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /reset"""
    user_id = str(update.effective_chat.id)
    cm.resetar(user_id)
    
    await update.message.reply_text(
        "🔄 Conversa reiniciada!\n\nDigite /start para começar de novo."
    )


# ============================================================================
# HANDLER DE MENSAGENS
# ============================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal de mensagens"""
    
    user_id = str(update.effective_chat.id)
    mensagem = update.message.text.strip()
    
    # Log
    print(f"📨 [{user_id}] {mensagem}")
    
    try:
        # Processar com ConversationManager
        resultado = cm.processar_mensagem(user_id, mensagem)
        
        resposta = resultado.get("resposta", "Erro ao processar.")
        
        # Log
        print(f"🤖 [{user_id}] {resposta[:100]}...")
        
        # Enviar resposta
        await update.message.reply_text(resposta, parse_mode="Markdown")
        
        # Se deve executar busca
        if resultado.get("executar_busca"):
            criterios = resultado.get("criterios", {})
            await executar_busca(update, user_id, criterios)
        
    except Exception as e:
        print(f"❌ Erro ao processar: {e}")
        await update.message.reply_text(
            "😕 Ops! Tive um problema.\n\nTente /reset ou /help"
        )


# ============================================================================
# EXECUTORES DE AÇÕES
# ============================================================================

async def executar_busca(
    update: Update,
    user_id: str,
    criterios: dict
):
    """Executa busca de produtos"""
    
    query = criterios.get("query", "")
    
    msg_busca = await update.message.reply_text(
        "🔍 Buscando produtos...\n⏳ Aguarde..."
    )
    
    try:
        # TODO: Integrar com SerpAPI e processador
        # Por enquanto, simular
        import time
        time.sleep(1)
        
        await msg_busca.edit_text(
            f"✅ Busca concluída!\n\n"
            f"🔍 Query: **{query}**\n\n"
            f"_Encontrei alguns produtos! (integração em desenvolvimento)_",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        await msg_busca.edit_text(
            "❌ Erro ao buscar produtos.\n\nTente novamente!"
        )


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Inicia o bot"""
    
    print("\n" + "="*60)
    print("🤖 SEXTA FEIRA - Telegram Bot")
    print("="*60)
    print(f"✅ Token configurado")
    print(f"✅ ConversationManager pronto")
    print("="*60 + "\n")
    
    # Criar aplicação
    app = Application.builder().token(TOKEN).build()
    
    # Registrar handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("ajuda", cmd_help))
    app.add_handler(CommandHandler("reset", cmd_reset))
    
    # Handler de mensagens de texto
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )
    
    # Iniciar
    print("✅ Bot iniciado! Aguardando mensagens...\n")
    print("   Pressione Ctrl+C para parar\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot encerrado!")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)