
import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
import traceback

# Bot logic ko yahan import karte hain
from quran_bot import (
    start,
    handle_message,
    CHOOSING_AYA,
    CHOOSING_BG,
    CHOOSING_RATIO,
    handle_background,
    handle_ratio
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

# Initialize bot application
application = Application.builder().token(BOT_TOKEN).build()

# Conversation handler to manage multi-step user interaction
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING_AYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        CHOOSING_BG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_background)],
        CHOOSING_RATIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ratio)],
    },
    fallbacks=[CommandHandler('start', start)]
)

application.add_handler(conv_handler)
application.add_handler(CommandHandler('start', start)) # Fallback

async def process_update(update_data):
    """Process a single update from the webhook"""
    update = Update.de_json(update_data, application.bot)
    await application.process_update(update)

@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    """Receive and process updates from Telegram"""
    update_data = request.get_json()
    if update_data:
        # Use asyncio to process the update
        asyncio.run(process_update(update_data))
        return jsonify({"status": "ok"})
    return jsonify({"status": "no data"}), 400

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

# Ensure the webhook is set automatically on startup
if WEBHOOK_URL:
    asyncio.run(application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}"))
