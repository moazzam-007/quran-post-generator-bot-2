import requests
import logging

logger = logging.getLogger(__name__)

async def get_ayah_data(surah, ayah):
    """Fetches Ayah data and page number from quran.com API."""
    try:
        # Fetching data
        api_url = f"https://api.quran.com/api/v4/verses/by_key/{surah}:{ayah}?language=en&fields=page_number"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Extracting data
        ayah_data = data['verses'][0]
        ayah_arabic = ayah_data['text']
        page_number = ayah_data['page']

        # Fetching English translation
        translation_api_url = f"https://api.quran.com/api/v4/verses/by_key/{surah}:{ayah}?language=en"
        translation_response = requests.get(translation_api_url)
        translation_response.raise_for_status()
        translation_data = translation_response.json()
        ayah_english = translation_data['verses'][0]['text']

        return {
            'surah_number': surah,
            'ayah_number': ayah,
            'ayah_arabic': ayah_arabic,
            'ayah_english': ayah_english,
            'page_number': page_number
        }
    except requests.RequestException as e:
        logger.error(f"API request error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error parsing API response: {e}")
        return None
