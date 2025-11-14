# 🧠 IntelliDash — Intelligent Multi-Source Dashboard

**IntelliDash** is a modern dashboard built with **Streamlit**, integrating multiple open APIs to deliver intelligent, data-driven insights from **weather**, **news**, **Wikipedia**, and **foreign exchange** — all enhanced with light **Natural Language Processing (NLP)**.

---

## 🚀 Features / Funcionalidades

### 🌦️ Weather (Open-Meteo)
- Real-time weather by city (temperature °C/°F, wind, UV index, sunrise & sunset).
- Powered by [Open-Meteo API](https://open-meteo.com/).

### 📚 Wikipedia
- Searches and summarizes Wikipedia topics.
- Extracts **keywords** (RAKE) and generates **summaries** (TextRank).
- Uses the [Wikipedia REST API](https://www.mediawiki.org/wiki/API:REST_API).

### 🗞️ Tech News (Hacker News)
- Retrieves the latest tech-related stories via [Hacker News Algolia API](https://hn.algolia.com/api).
- Performs a **sentiment score** analysis for each title.

### 💱 Currency Exchange (Frankfurter.app)
- Converts between major currencies and shows **historical exchange rates (7 days)**.
- Uses [Frankfurter.app](https://www.frankfurter.app/) — ✅ **no API key required**.

### 🧠 NLP Intelligence
- Keyword extraction (RAKE)
- Summarization (TextRank)
- Heuristic sentiment analysis

---

## 🧩 Architecture Overview

Streamlit App
├── app.py ← Main dashboard logic and UI
├── services/
│ ├── weather.py ← Open-Meteo API (forecast + geocoding)
│ ├── wiki.py ← Wikipedia summaries + search
│ ├── news.py ← Hacker News API integration
│ ├── forex.py ← Frankfurter API (conversion + timeseries)
│
└── intelligence/
└── nlp.py ← RAKE, TextRank & sentiment functions

yaml
Copiar código

---

## 🖥️ Run Locally / Ejecutar en local

### 🪄 1. Create and activate a virtual environment
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1     # On Windows PowerShell
# or
source .venv/bin/activate        # On macOS / Linux
📦 2. Install dependencies
bash
Copiar código
pip install -r requirements.txt
▶️ 3. Run IntelliDash
bash
Copiar código
streamlit run app.py
Then open http://localhost:8501 in your browser.

🐳 Run in Docker / Ejecutar con Docker
bash
Copiar código
docker compose up --build
Once running, visit http://localhost:8501.
To stop the container:

bash
Copiar código
docker compose down
🔍 Example Queries / Ejemplos de uso
Tab	Example Input	Output
🌍 Smart Search	“Barcelona”	Combined Weather + Wiki + News + FX info
📚 Wikipedia	“Artificial Intelligence”	Summary + Keywords + Auto-summary
🗞️ News	“AI”	Top Hacker News results
⛅ Weather	“Tokyo”	Temperature, UV, sunrise/sunset
💱 FX Converter	100 EUR → USD	Real-time conversion + historical chart

🧾 License / Licencia
This project is released under the MIT License — you’re free to use, modify, and distribute with attribution.
El proyecto se distribuye bajo licencia MIT, libre para uso y modificación con atribución.

✨ Credits / Créditos
Developed with ❤️ using:

Streamlit

Pandas

NetworkX

Open-Meteo API

Wikipedia REST API

Hacker News Algolia API

Frankfurter.app

yaml
Copiar código

---
