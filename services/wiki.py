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

        resp = requests.get(
            SEARCH_URL,
            params={"q": query, "limit": limit},
            headers=HEADERS,
            timeout=10,
        )

    except requests.RequestException as e:

        return []

    if resp.status_code != 200:

        return []

    try:
        data = resp.json()
    except ValueError as e:

        return []


    # Different versions of the API might use 'pages' or 'data'
    pages = data.get("pages") or data.get("data") or []


    return pages


def get_summary(title: str) -> Optional[Dict[str, Any]]:
    """Get the summary JSON for a given Wikipedia page title."""
    from urllib.parse import quote

    url = BASE_SUMMARY + quote(title)


    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)

    except requests.RequestException as e:

        return None

    if resp.status_code != 200:

        return None

    try:
        data = resp.json()
    except ValueError as e:

        return None

    #rint(f"[DEBUG] Summary JSON keys: {list(data.keys())}")
    return data

def _classify_from_summary(summary: Dict[str, Any]) -> str:
    """
    Decide if the summary describes a place, a person, or something else.
    Returns: 'place' | 'person' | 'unknown'
    """
    # Use both the short description and the longer extract
    text = (
        (summary.get("description") or "") + " " +
        (summary.get("extract") or "")
    ).lower()

    # Heuristics for places
    place_keywords = [
        "city", "town", "village", "country", "region", "province", "state",
        "county", "district", "island", "mountain", "river", "lake", "park",
        "municipality", "suburb", "neighborhood", "capital", "airport",
        "railway station", "metro station",
    ]
    if any(kw in text for kw in place_keywords):
        return "place"

    # Heuristics for people / names / surnames
    person_keywords = [
        "surname", "family name", "given name", "person", "footballer",
        "politician", "actor", "actress", "singer", "musician", "writer",
        "novelist", "poet", "scientist", "physicist", "mathematician",
        "chemist", "engineer", "entrepreneur", "businessman", "businesswoman",
        "model", "director", "born ",
    ]
    if any(kw in text for kw in person_keywords):
        return "person"

    return "unknown"


def infer_entity_type_from_pages(pages: List[Dict[str, Any]]) -> str:
    """
    Given the Wikipedia search results, infer what the query most likely is:
    'place', 'person', or 'unknown'.
    We look at the first result's summary.
    """
    if not pages:
        return "unknown"

    title = pages[0].get("title") or pages[0].get("key") or ""
    if not title:
        return "unknown"

    try:
        summary = get_summary(title)
    except Exception:
        return "unknown"

    if not summary:
        return "unknown"

    return _classify_from_summary(summary)

# if __name__ == "__main__":
#     # Example debug run
#     query = "Python"
#     pages = search_pages(query, limit=3)

#     if not pages:
#         print("[INFO] No pages returned from search.")
#     else:
#         for idx, p in enumerate(pages, start=1):
#             title = p.get("title") or p.get("key") or "<no-title>"
#             print(f"\n=== Result {idx} ===")
#             print(f"Title: {title}")

#             summary = get_summary(title)
#             if summary is None:
#                 print("[INFO] No summary returned.")
#             else:
#                 extract = summary.get("extract") or ""
#                 print(f"Summary (first 200 chars): {extract[:200]!r}")
