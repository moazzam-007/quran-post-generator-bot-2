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

async def process_update(update_data):
    """Process a single update from the webhook"""
    try:
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        logger.error(traceback.format_exc())

@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    """Receive and process updates from Telegram"""
    try:
        update_data = request.get_json()
        if update_data:
            # Create new event loop for this request
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(process_update(update_data))
            loop.close()
            return jsonify({"status": "ok"})
        return jsonify({"status": "no data"}), 400
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook_route():
    """Set webhook URL"""
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    try:
        # Create new event loop for webhook setup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.bot.set_webhook(url=webhook_url))
        loop.close()
        return f"Webhook set to {webhook_url}"
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return f"Error setting webhook: {e}", 500

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/')
def home():
    return '<h1>Quran Bot is running!</h1>'

if __name__ == '__main__':
    # Local development ke liye
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
