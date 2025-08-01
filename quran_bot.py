import logging
import re
import os
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
    try:
        await update.message.reply_text(
            "🕌 Assalamu Alaikum! Main aapke liye Quran ki Ayah ka beautiful post bana sakta hoon.\n\n"
            "📖 Kripya Surah aur Ayah number dalein (jaise: 1,1)\n"
            "❌ Cancel karne ke liye 'cancel' type karein."
        )
        return CHOOSING_AYA
    except Exception as e:
        logger.error(f"Error in start function: {e}")
        return ConversationHandler.END

async def handle_ayah_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles user input for Surah and Ayah number."""
    try:
        user_input = update.message.text.strip()
        
        if user_input.lower() == 'cancel':
            await update.message.reply_text('Operation cancelled. /start karke dobara shuru kar sakte hain.')
            return ConversationHandler.END

        # Better regex pattern to handle different formats
        match = re.match(r'^(\d+)[,:\-\s]+(\d+)$', user_input)
        
        if match:
            surah, ayah = map(int, match.groups())
            
            # Validate surah and ayah numbers
            if surah < 1 or surah > 114:
                await update.message.reply_text(
                    "❌ Surah number 1 se 114 ke beech hona chahiye. Dobara try karein."
                )
                return CHOOSING_AYA
                
            if ayah < 1:
                await update.message.reply_text(
                    "❌ Ayah number 1 se zyada hona chahiye. Dobara try karein."
                )
                return CHOOSING_AYA
            
            context.user_data['surah'] = surah
            context.user_data['ayah'] = ayah
            
            reply_keyboard = [['🤍 White BG', '🖤 Black BG']]
            await update.message.reply_text(
                f"✅ Surah {surah}, Ayah {ayah} selected!\n\n🎨 Kripya background choose karein:",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            )
            return CHOOSING_BG
        else:
            await update.message.reply_text(
                "❌ Format galat hai!\n\n"
                "✅ Sahi format: 'surah,ayah' (jaise: 1,1 ya 2:5 ya 3-10)\n"
                "🔄 Dobara try karein:"
            )
            return CHOOSING_AYA
    except Exception as e:
        logger.error(f"Error in handle_ayah_input: {e}")
        await update.message.reply_text("❌ Koi error hui hai. Dobara try karein ya /start karein.")
        return ConversationHandler.END

async def handle_background(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles user choice for background."""
    try:
        bg_choice = update.message.text.lower()
        
        if 'white' in bg_choice:
            context.user_data['background'] = 'white'
        elif 'black' in bg_choice:
            context.user_data['background'] = 'black'
        else:
            await update.message.reply_text(
                "❌ Invalid choice! Kripya button use karein ya 'White BG' / 'Black BG' type karein."
            )
            return CHOOSING_BG

        reply_keyboard = [['📱 1:1 (Instagram Post)', '📲 4:5 (Instagram Story)']]
        await update.message.reply_text(
            f"✅ {context.user_data['background'].title()} background selected!\n\n"
            "📐 Kripya image ka aspect ratio choose karein:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return CHOOSING_RATIO
    except Exception as e:
        logger.error(f"Error in handle_background: {e}")
        await update.message.reply_text("❌ Koi error hui hai. Dobara try karein.")
        return CHOOSING_BG

async def handle_ratio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles user choice for aspect ratio and generates the image."""
    try:
        ratio_choice = update.message.text.lower()
        
        if '1:1' in ratio_choice:
            context.user_data['ratio'] = '1:1'
        elif '4:5' in ratio_choice:
            context.user_data['ratio'] = '4:5'
        else:
            await update.message.reply_text(
                "❌ Invalid choice! Kripya button use karein ya '1:1' / '4:5' type karein."
            )
            return CHOOSING_RATIO

        surah = context.user_data['surah']
        ayah = context.user_data['ayah']
        background = context.user_data['background']
        ratio = context.user_data['ratio']

        await update.message.reply_text(
            "🎨 Post taiyar ho raha hai...\n⏳ Kripya thoda intezar karein...", 
            reply_markup=ReplyKeyboardRemove()
        )

        # Fetch ayah data
        ayah_data = await get_ayah_data(surah, ayah)
        
        if ayah_data:
            # Generate image
            image_path = generate_quran_image(ayah_data, background, ratio)
            
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as image_file:
                    await update.message.reply_photo(
                        photo=image_file,
                        caption=f"🕌 Surah {surah}, Ayah {ayah}\n"
                               f"🎨 {background.title()} background, {ratio} ratio\n\n"
                               f"✨ /start karke naya post banayiye!"
                    )
                
                # Clean up file after sending
                try:
                    os.remove(image_path)
                except:
                    pass
                    
            else:
                await update.message.reply_text(
                    "❌ Image generate nahi ho payi. Kripya dobara try karein.\n\n"
                    "🔄 /start karke naya attempt karein."
                )
        else:
            await update.message.reply_text(
                "❌ Ayah data fetch nahi ho paya.\n"
                "🔍 Kripya Surah aur Ayah number check karein.\n\n"
                "🔄 /start karke dobara try karein."
            )

        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in handle_ratio: {e}")
        await update.message.reply_text(
            "❌ Koi technical error hui hai.\n"
            "🔄 /start karke dobara try karein."
        )
        return ConversationHandler.END
