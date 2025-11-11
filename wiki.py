import requests
from typing import Optional, Dict, Any, List

BASE = "https://en.wikipedia.org/api/rest_v1/page/summary/"
SEARCH = "https://en.wikipedia.org/w/rest.php/v1/search/title"

def search_pages(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    r = requests.get(SEARCH, params={"q": query, "limit": limit}, timeout=10)
    if r.status_code != 200:
        return []
    js = r.json()
    return js.get("pages", [])

def get_summary(title: str) -> Optional[Dict[str, Any]]:
    url = BASE + requests.utils.quote(title)
    r = requests.get(url, timeout=10, headers={"accept": "application/json"})
    if r.status_code != 200:
        return None
    return r.json()