from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import logging

logger = logging.getLogger(__name__)

# Fonts
TRANSLATION_FONT = ImageFont.truetype(os.path.join('fonts', 'Geogery_SemiBold.ttf'), size=24)
BSML_FONT = ImageFont.truetype(os.path.join('fonts', 'QCF_BSML.ttf'), size=36) # For Bismillah

def get_arabic_font_for_page(page_number):
    """Selects the correct font file for a given page number."""
    # Assuming file names are like QCF_P001.ttf
    font_file_name = f'QCF_P{page_number:03d}.ttf'
    font_path = os.path.join('fonts', font_file_name)
    try:
        return ImageFont.truetype(font_path, size=48)
    except Exception as e:
        logger.error(f"Could not load font for page {page_number}: {e}")
        return ImageFont.load_default()

def generate_quran_image(ayah_data, background, ratio):
    """Generates an image with Ayah and translation."""
    
    if ratio == '1:1':
        width, height = 1080, 1080
    else: # 4:5
        width, height = 1080, 1350

    if background == 'black':
        bg_color, text_color = (0, 0, 0), (255, 255, 255)
    else:
        bg_color, text_color = (255, 255, 255), (0, 0, 0)
    
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    padding = int(width * 0.05)
    
    # Arabic text
    ayah_arabic = ayah_data['ayah_arabic']
    ayah_english = ayah_data['ayah_english']
    page_number = ayah_data['page_number']
    
    # Arabic text (right-aligned)
    arabic_font = get_arabic_font_for_page(page_number)
    draw.text((width - padding, padding), ayah_arabic, font=arabic_font, fill=text_color, anchor="rt")

    # Translation text (center-aligned)
    translation_text_wrapped = textwrap.wrap(ayah_english, width=50) # Wrap long lines
    translation_text = "\n".join(translation_text_wrapped)
    
    # Calculate text position to be below Arabic
    arabic_text_bbox = draw.textbbox((width - padding, padding), ayah_arabic, font=arabic_font, anchor="rt")
    translation_y_start = arabic_text_bbox[3] + padding
    
    translation_text_position = (width / 2, translation_y_start)
    draw.multiline_text(translation_text_position, translation_text, font=TRANSLATION_FONT, fill=text_color, align="center", anchor="ma")
    
    # Create output folder if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')

    output_path = f'output/{ayah_data["surah_number"]}_{ayah_data["ayah_number"]}_{background}_{ratio.replace(":", "x")}.jpg'
    image.save(output_path)
    return output_path
