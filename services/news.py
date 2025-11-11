import requests
from typing import List, Dict, Any

BASE = "https://hn.algolia.com/api/v1/search"

def search_hn(query: str, hits_per_page: int = 10) -> List[Dict[str, Any]]:
    r = requests.get(BASE, params={"query": query, "tags": "story", "hitsPerPage": hits_per_page}, timeout=10)
    if r.status_code != 200:
        return []
    js = r.json()
    return js.get("hits", [])
