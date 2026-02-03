import json
import urllib.request
import logging

logger = logging.getLogger(__name__)

def get_weather_condition_korean(wmo_code):
    """
    Maps WMO Weather Codes to Korean.
    Ref: https://open-meteo.com/en/docs
    """
    if wmo_code == 0: return "맑음"
    if wmo_code in [1, 2, 3]: return "구름 많음"
    if wmo_code in [45, 48]: return "안개"
    if wmo_code in [51, 53, 55, 61, 63, 65]: return "비"
    if wmo_code in [56, 57, 66, 67]: return "진눈깨비"
    if wmo_code in [71, 73, 75, 77]: return "눈"
    if wmo_code in [80, 81, 82]: return "소나기"
    if wmo_code in [85, 86]: return "눈 (강함)"
    if wmo_code >= 95: return "뇌우"
    return "흐림"

def fetch_real_time_weather(lat=37.5665, lon=126.9780):
    """
    Fetches real-time weather from Open-Meteo API (Free, No Key).
    Default: Seoul (37.5665, 126.9780)
    Returns: (condition_str, temp_float) or (None, None) on failure.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                current = data.get('current_weather', {})
                
                temp = current.get('temperature')
                code = current.get('weathercode')
                
                condition = get_weather_condition_korean(code)
                return condition, temp
            
    except Exception as e:
        logger.error(f"Weather API Error: {e}")
        
    return None, None
