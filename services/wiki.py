import requests
from typing import Optional, Dict, Any, List

BASE_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"
SEARCH_URL   = "https://en.wikipedia.org/w/rest.php/v1/search/title"

# Always send a sensible User-Agent to Wikipedia
HEADERS = {
    "accept": "application/json",
    "User-Agent": "MyWikiClient/0.1 (example@example.com)"
}

def search_pages(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search Wikipedia page titles and return the raw page dicts."""
    try:
        print(f"[DEBUG] Searching for: {query!r}, limit={limit}")
        resp = requests.get(
            SEARCH_URL,
            params={"q": query, "limit": limit},
            headers=HEADERS,
            timeout=10,
        )
        print(f"[DEBUG] Search URL: {resp.url}")
        print(f"[DEBUG] Status code: {resp.status_code}")
    except requests.RequestException as e:
        print(f"[ERROR] Request to search endpoint failed: {e}")
        return []

    if resp.status_code != 200:
        print("[ERROR] Non-200 response from search endpoint")
        print(f"[DEBUG] Response text (first 500 chars): {resp.text[:500]!r}")
        return []

    try:
        data = resp.json()
    except ValueError as e:
        print(f"[ERROR] Failed to decode JSON: {e}")
        print(f"[DEBUG] Raw response text (first 500 chars): {resp.text[:500]!r}")
        return []

    print(f"[DEBUG] Top-level JSON keys: {list(data.keys())}")

    # Different versions of the API might use 'pages' or 'data'
    pages = data.get("pages") or data.get("data") or []
    print(f"[DEBUG] Number of pages found: {len(pages)}")

    return pages


def get_summary(title: str) -> Optional[Dict[str, Any]]:
    """Get the summary JSON for a given Wikipedia page title."""
    from urllib.parse import quote

    url = BASE_SUMMARY + quote(title)
    print(f"[DEBUG] Getting summary for title: {title!r}")
    print(f"[DEBUG] Summary URL: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        print(f"[DEBUG] Status code: {resp.status_code}")
    except requests.RequestException as e:
        print(f"[ERROR] Request to summary endpoint failed: {e}")
        return None

    if resp.status_code != 200:
        print("[ERROR] Non-200 response from summary endpoint")
        print(f"[DEBUG] Response text (first 500 chars): {resp.text[:500]!r}")
        return None

    try:
        data = resp.json()
    except ValueError as e:
        print(f"[ERROR] Failed to decode JSON for summary: {e}")
        print(f"[DEBUG] Raw response text (first 500 chars): {resp.text[:500]!r}")
        return None

    print(f"[DEBUG] Summary JSON keys: {list(data.keys())}")
    return data


if __name__ == "__main__":
    # Example debug run
    query = "Python"
    pages = search_pages(query, limit=3)

    if not pages:
        print("[INFO] No pages returned from search.")
    else:
        for idx, p in enumerate(pages, start=1):
            title = p.get("title") or p.get("key") or "<no-title>"
            print(f"\n=== Result {idx} ===")
            print(f"Title: {title}")

            summary = get_summary(title)
            if summary is None:
                print("[INFO] No summary returned.")
            else:
                extract = summary.get("extract") or ""
                print(f"Summary (first 200 chars): {extract[:200]!r}")
    