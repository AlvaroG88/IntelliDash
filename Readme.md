# IntelliDash — Intelligent Multi-Source Dashboard (Streamlit)

App con GUI que consulta 4 APIs públicas (sin API keys):
1. Open-Meteo (tiempo)
2. Wikipedia REST (resúmenes)
3. Hacker News Algolia (noticias tech)
4. exchangerate.host (divisas)

Incluye NLP ligero: keywords (RAKE), resumen (TextRank), y sentimiento heurístico.

## Uso
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py