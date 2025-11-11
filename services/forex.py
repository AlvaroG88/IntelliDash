import requests
from typing import Dict, Any, Optional

BASE = "https://api.exchangerate.host"

def convert(amount: float, base: str, target: str) -> Optional[Dict[str, Any]]:
    r = requests.get(f"{BASE}/convert", params={"from": base.upper(), "to": target.upper(), "amount": amount}, timeout=10)
    if r.status_code != 200:
        return None
    return r.json()

def timeseries(base: str, target: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
    r = requests.get(f"{BASE}/timeseries", params={"base": base.upper(), "symbols": target.upper(),
                                                   "start_date": start_date, "end_date": end_date}, timeout=10)
    if r.status_code != 200:
        return None
    return r.json()
