import requests
import pandas as pd
import datetime as dt
from typing import Dict, Any, Optional, List

BASE = "https://api.frankfurter.app"

def convert_currency(amount: float, base: str, target: str) -> Dict[str, Any]:
    """Convierte divisas usando api.frankfurter.app (sin API key)."""
    try:
        # Evitar error si las divisas son iguales
        if base.upper() == target.upper():
            return {
                "success": True,
                "result": amount,
                "rate": 1.0,
                "query": {"from": base.upper(), "to": target.upper()},
            }

        url = f"{BASE}/latest"
        params = {"from": base.upper(), "to": target.upper()}
        r = requests.get(url, params=params, timeout=10)
        js = r.json()

        if "rates" not in js or target.upper() not in js["rates"]:
            return {"success": False, "error": "Invalid response", "raw": js}

        rate = js["rates"][target.upper()]
        result = amount * rate
        return {
            "success": True,
            "result": result,
            "rate": rate,
            "query": {"from": base.upper(), "to": target.upper()},
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_timeseries(base: str, target: str, days: int = 7) -> Optional[pd.DataFrame]:
    """Obtiene tasas históricas reales de los últimos X días."""
    try:
        end = dt.date.today()
        start = end - dt.timedelta(days=days)
        url = f"{BASE}/{start.isoformat()}..{end.isoformat()}"
        params = {"from": base.upper(), "to": target.upper()}
        r = requests.get(url, params=params, timeout=10)
        js = r.json()

        if "rates" not in js:
            return None

        rates = js["rates"]
        df = pd.DataFrame({
            "date": pd.to_datetime(list(rates.keys())),
            "rate": [v[target.upper()] for v in rates.values()],
        }).set_index("date").sort_index()
        return df
    except Exception:
        return None

def get_common_currencies() -> List[str]:
    """Devuelve lista de códigos de divisas comunes."""
    return [
        "EUR", "USD", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD",
        "CNY", "HKD", "SEK", "NOK", "DKK", "PLN", "MXN", "BRL",
        "INR", "SGD", "ZAR", "KRW"
    ]
