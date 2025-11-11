import requests
from typing import Optional, Dict, Any

BASE = "https://api.open-meteo.com/v1/forecast"
GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"

def geocode_city(city: str) -> Optional[Dict[str, Any]]:
    r = requests.get(GEOCODE, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=10)
    if r.status_code != 200:
        return None
    js = r.json()
    if not js.get("results"):
        return None
    return js["results"][0]

def get_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,cloud_cover,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,uv_index_max",
        "timezone": "auto",
    }
    r = requests.get(BASE, params=params, timeout=15)
    if r.status_code != 200:
        return None
    return r.json()
