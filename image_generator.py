from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import logging

logger = logging.getLogger(__name__)

# Fonts
try:
    ARABIC_FONT_FILES = {f'p{i}.ttf' for i in range(1, 606)}
    # Add your Geogery SemiBold font file here
    TRANSLATION_FONT = ImageFont.truetype(os.path.join('fonts', 'Geogery_SemiBold.ttf'), size=24)
except Exception as e:
    logger.error(f"Error loading fonts: {e}")
    # Fallback fonts
    ARABIC_FONT_FILES = {}
    TRANSLATION_FONT = ImageFont.load_default()

def get_arabic_font_for_page(page_number):
    """Selects the correct font file for a given page number."""
    font_file_name = f'QCF_P{page_number:03d}.ttf' # assuming file names are like QCF_P001.ttf
    font_path = os.path.join('fonts', font_file_name)
    try:
        return ImageFont.truetype(font_path, size=48)
    except Exception as e:
        logger.error(f"Could not load font for page {page_number}: {e}")
        return ImageFont.load_default()

def generate_quran_image(ayah_data, background, ratio):
    """Generates an image with Ayah and translation."""
    
    # Image dimensions
    if ratio == '1:1':
        width, height = 1080, 1080
    else: # 4:5
        width, height = 1080, 1350

    # Colors
    if background == 'black':
        bg_color, text_color = (0, 0, 0), (255, 255, 255)
    else:
        bg_color, text_color = (255, 255, 255), (0, 0, 0)
    
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Padding
    padding = int(width * 0.05)
    
    # Text
    ayah_arabic = ayah_data['ayah_arabic']
    ayah_english = ayah_data['ayah_english']
    
    # Arabic text (right-aligned)
    arabic_font = get_arabic_font_for_page(ayah_data['page_number'])
    arabic_text_bbox = draw.textbbox((0, 0), ayah_arabic, font=arabic_font)
    arabic_text_width = arabic_text_bbox[2] - arabic_text_bbox[0]
    arabic_text_position = (width - padding - arabic_text_width, padding)
    draw.text(arabic_text_position, ayah_arabic, font=arabic_font, fill=text_color, align="right")
    
    # Translation text (center-aligned)
    translation_text_position = (padding, padding + arabic_text_bbox[3] - arabic_text_bbox[1] + 20)
    draw.text(translation_text_position, ayah_english, font=TRANSLATION_FONT, fill=text_color, align="center")
    
    # Save image
    output_path = f'output/{ayah_data["surah_number"]}_{ayah_data["ayah_number"]}.jpg'
    image.save(output_path)
    return output_path
