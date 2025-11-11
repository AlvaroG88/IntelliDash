# IntelliDash — Intelligent Multi-Source Dashboard (Streamlit)

Python App with GUI consulting 4 public APIs:
1. Open-Meteo (weather)
2. Wikipedia REST (summaries)
3. Hacker News Algolia (tech news)
4. exchangerate.host (exhange)

Incluye NLP ligero: keywords (RAKE), resumen (TextRank), y sentimiento heurístico.

## Uso
```bash
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

streamlit run app.py
