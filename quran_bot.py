import logging
import re
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from image_generator import generate_quran_image
from data_fetcher import get_ayah_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Conversation states
CHOOSING_AYA, CHOOSING_BG, CHOOSING_RATIO = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends a message with options for Surah and Ayah."""
    await update.message.reply_text(
        "Assalamu Alaikum! Main aapke liye Quran ki Ayah ka post bana sakta hoon. "
        "Kripya Surah aur Ayah number dalein (jaise: 1,1)."
    )
    return CHOOSING_AYA

async def handle_ayah_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles user input for Surah and Ayah number."""
    user_input = update.message.text
    if user_input.lower() == 'cancel':
        await update.message.reply_text('Operation cancelled.')
        return ConversationHandler.END

    match = re.match(r'(\d+),(\d+)', user_input.strip())
    if match:
        surah, ayah = map(int, match.groups())
        context.user_data['surah'] = surah
        context.user_data['ayah'] = ayah
        
        reply_keyboard = [['White BG', 'Black BG']]
        await update.message.reply_text(
            "Kripya background choose karein:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return CHOOSING_BG
    else:
        await update.message.reply_text(
            "Maafi chahata hoon, aapka format galat hai. Kripya Surah aur Ayah number 'surah,ayah' format mein daalein (jaise: 1,1)."
        )
        return CHOOSING_AYA

async def handle_background(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles user choice for background."""
    bg_choice = update.message.text.lower()
    if 'white' in bg_choice:
        context.user_data['background'] = 'white'
    elif 'black' in bg_choice:
        context.user_data['background'] = 'black'
    else:
        await update.message.reply_text("Maafi chahata hoon, background color invalid hai. Kripya 'White BG' ya 'Black BG' chune.")
        return CHOOSING_BG

    reply_keyboard = [['1:1', '4:5']]
    await update.message.reply_text(
        "Kripya image ka aspect ratio choose karein:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSING_RATIO

async def handle_ratio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles user choice for aspect ratio and generates the image."""
    ratio_choice = update.message.text
    if '1:1' in ratio_choice:
        context.user_data['ratio'] = '1:1'
    elif '4:5' in ratio_choice:
        context.user_data['ratio'] = '4:5'
    else:
        await update.message.reply_text("Maafi chahata hoon, ratio invalid hai. Kripya '1:1' ya '4:5' chune.")
        return CHOOSING_RATIO

    surah = context.user_data['surah']
    ayah = context.user_data['ayah']
    background = context.user_data['background']
    ratio = context.user_data['ratio']

    await update.message.reply_text("Post taiyar ho raha hai, kripya thoda intezar karein...", reply_markup=ReplyKeyboardRemove())
    
    ayah_data = await get_ayah_data(surah, ayah)
    
    if ayah_data:
        image_path = generate_quran_image(ayah_data, background, ratio)
        if image_path:
            with open(image_path, 'rb') as image_file:
                await update.message.reply_photo(photo=image_file)
            await update.message.reply_text(f"Output saved as: {image_path}")
        else:
            await update.message.reply_text("Maafi chahata hoon, image generate nahi ho payi.")
    else:
        await update.message.reply_text("Maafi chahata hoon, data fetch nahi ho paya. Kripya Surah aur Ayah number check karein.")

    return ConversationHandler.END
