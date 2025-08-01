import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import asyncio
import traceback

# Bot logic ko yahan import karte hain
from quran_bot import (
    start,
    handle_ayah_input,
    handle_background,
    handle_ratio,
    CHOOSING_AYA,
    CHOOSING_BG,
    CHOOSING_RATIO
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Environment variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
    raise ValueError("TELEGRAM_BOT_TOKEN is required.")

if not WEBHOOK_URL:
    logger.error("WEBHOOK_URL environment variable is not set!")
    raise ValueError("WEBHOOK_URL is required.")

# Application object ko globally banate hain
application = Application.builder().token(BOT_TOKEN).build()

# Conversation handler to manage multi-step user interaction
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING_AYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ayah_input)],
        CHOOSING_BG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_background)],
        CHOOSING_RATIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ratio)],
    },
    fallbacks=[CommandHandler('start', start)]
)

application.add_handler(conv_handler)
application.add_handler(CommandHandler('start', start))

@app.route("/" + BOT_TOKEN, methods=["POST"])
async def webhook():
    """Receive and process updates from Telegram"""
    try:
        update_data = request.get_json()
        if update_data:
            update = Update.de_json(update_data, application.bot)
            await application.process_update(update)
            return jsonify({"status": "ok"})
        return jsonify({"status": "no data"}), 400
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set_webhook')
async def set_webhook_route():
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    try:
        await application.bot.set_webhook(url=webhook_url)
        return f"Webhook set to {webhook_url}"
    except Exception as e:
        return f"Error setting webhook: {e}"

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})
    
@app.route('/')
def home():
    return '<h1>Quran Bot is running!</h1>'
