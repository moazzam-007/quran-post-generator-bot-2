from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Fonts ke liye ek lru_cache use kar rahe hain taaki har baar font load na karna pade.
@lru_cache(maxsize=128)
def get_translation_font(size):
    try:
        return ImageFont.truetype(os.path.join('fonts', 'Geogery_SemiBold.ttf'), size=size)
    except Exception as e:
        logger.error(f"Could not load Geogery_SemiBold.ttf: {e}")
        return ImageFont.load_default()

@lru_cache(maxsize=650)
def get_arabic_font_for_page(page_number):
    """Selects the correct font file for a given page number."""
    try:
        # User ne bataya ki files p1.ttf se p605.ttf ke naam se hain
        # Agar Bismillah font hai to use bhi handle karenge
        if page_number == 0:
             font_file_name = 'QCF_BSML.ttf'
        else:
             font_file_name = f'QCF_P{page_number:03d}.ttf' # <-- File name ka format sahi kiya
             
        font_path = os.path.join('fonts', font_file_name)

        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size=48)
        else:
            logger.warning(f"Font file not found: {font_path}")
            # Fallback to general font (p001.ttf) if specific page font is missing
            fallback_path = os.path.join('fonts', 'QCF_P001.ttf')
            if os.path.exists(fallback_path):
                return ImageFont.truetype(fallback_path, size=48)
            else:
                return ImageFont.load_default()
    except Exception as e:
        logger.error(f"Could not load font for page {page_number}: {e}")
        return ImageFont.load_default()

def generate_quran_image(ayah_data, background, ratio):
    """Generates an image with Ayah and translation."""
    try:
        # Set dimensions
        if ratio == '1:1':
            width, height = 1080, 1080
        else:  # 4:5
            width, height = 1080, 1350

        # Set colors
        if background == 'black':
            bg_color, text_color = (0, 0, 0), (255, 255, 255)
        else:
            bg_color, text_color = (255, 255, 255), (0, 0, 0)

        # Create image
        image = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)

        padding = int(width * 0.05)
        
        ayah_arabic = ayah_data.get('ayah_arabic', '')
        ayah_english = ayah_data.get('ayah_english', '')
        page_number = ayah_data.get('page_number', 1)
        surah_number = ayah_data.get('surah_number', 1)
        ayah_number = ayah_data.get('ayah_number', 1)

        # Get fonts
        arabic_font = get_arabic_font_for_page(page_number)
        translation_font = get_translation_font(size=28) # Font size adjust kiya
        
        # Bismillah ko handle karna
        if surah_number != 1 and ayah_number == 1:
            bismillah_text = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ"
            bismillah_font = get_arabic_font_for_page(0) # Special BSML font
            bismillah_bbox = draw.textbbox((width / 2, padding), bismillah_text, font=bismillah_font, anchor="ma")
            draw.text((width / 2, padding), bismillah_text, font=bismillah_font, fill=text_color, align="center", anchor="ma")
            arabic_y_start = bismillah_bbox[3] + padding
        else:
            arabic_y_start = padding

        # Arabic text (right-aligned, with text wrapping)
        arabic_text_lines = textwrap.wrap(ayah_arabic, width=int(width*0.8/arabic_font.size*2.5)) # Dynamic line width
        line_height = arabic_font.size * 1.5
        y = arabic_y_start
        for line in arabic_text_lines:
            draw.text((width - padding, y), line, font=arabic_font, fill=text_color, anchor="rt")
            y += line_height

        # Translation text (center-aligned, below Arabic)
        translation_text_wrapped = textwrap.wrap(ayah_english, width=45)
        translation_text = "\n".join(translation_text_wrapped)
        
        translation_y_start = y + padding
        translation_position = (width // 2, translation_y_start)
        draw.multiline_text(translation_position, translation_text, font=translation_font, fill=text_color, align="center", anchor="ma")
        
        # Add reference at bottom
        reference_text = f"Quran {surah_number}:{ayah_number}"
        reference_y = height - padding
        reference_font = get_translation_font(size=20)
        draw.text((width // 2, reference_y), reference_text, font=reference_font, fill=text_color, align="center", anchor="ma")

        # Create output directory
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save image
        output_path = f'{output_dir}/{surah_number}_{ayah_number}_{background}_{ratio.replace(":", "x")}.jpg'
        image.save(output_path, 'JPEG', quality=95)
        
        logger.info(f"Image generated successfully: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return None
