import requests
import logging
import asyncio

logger = logging.getLogger(__name__)

async def get_ayah_data(surah, ayah):
    """Fetches Ayah data and page number from quran.com API."""
    try:
        # Fetching Arabic text and page number
        api_url = f"https://api.quran.com/api/v4/verses/by_key/{surah}:{ayah}?language=en&fields=page_number"
        
        # Use asyncio to make non-blocking request
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get, api_url)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('verses') or len(data['verses']) == 0:
            logger.error(f"No verses found for {surah}:{ayah}")
            return None
            
        # Extracting data
        ayah_data = data['verses'][0]
        ayah_arabic = ayah_data.get('text', '')
        page_number = ayah_data.get('page', 1)

        # Fetching English translation
        translation_api_url = f"https://api.quran.com/api/v4/verses/by_key/{surah}:{ayah}?language=en&translations=131"
        
        translation_response = await loop.run_in_executor(None, requests.get, translation_api_url)
        translation_response.raise_for_status()
        
        translation_data = translation_response.json()
        
        if translation_data.get('verses') and len(translation_data['verses']) > 0:
            ayah_english = translation_data['verses'][0].get('text', 'Translation not available')
        else:
            ayah_english = 'Translation not available'

        # Clean up HTML tags from translation if any
        import re
        ayah_english = re.sub(r'<[^>]+>', '', ayah_english)

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
