#!/usr/bin/env python3
"""Run Telegram bot using ConversationManager and python-telegram-bot (polling).

Usage:
    source .env
    python3 run_telegram.py
"""
import os
import sys
PROJECT_ROOT = os.path.dirname(__file__)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.config import ConversationManager
from utils.logger import LoggerManager

# Import telegram only when running
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except Exception:
    raise SystemExit("python-telegram-bot not installed. Install with `pip install python-telegram-bot`")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise SystemExit("TELEGRAM_BOT_TOKEN not set in environment (.env)")

cm = ConversationManager()
logger = LoggerManager().obter("telegram")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    nome = update.effective_user.first_name or "Cliente"
    resp = cm.iniciar_conversa(user_id, nome)
    await update.message.reply_text(resp)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start to iniciar, /reset para reiniciar a sessão.")

async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    cm.resetar(user_id)
    await update.message.reply_text("Sessão reiniciada.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    mensagem = update.message.text
    logger.user(mensagem)
    resultado = cm.processar_mensagem(user_id, mensagem)
    await update.message.reply_text(resultado.get("resposta"))
    logger.bot(resultado.get("resposta"))


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Starting Telegram bot... (Press Ctrl+C to stop)")
    app.run_polling()


if __name__ == '__main__':
    main()
