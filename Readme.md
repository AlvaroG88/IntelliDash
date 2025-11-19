# 🧠 IntelliDash — Intelligent Multi-Source Dashboard

**IntelliDash** is a modern dashboard built with **Streamlit**, integrating multiple open APIs to deliver intelligent, data-driven insights from **weather**, **news**, **Wikipedia**, and **foreign exchange** — all enhanced with light **Natural Language Processing (NLP)**.

---

## Features

### Weather (Open-Meteo)
- Real-time weather by city (temperature °C/°F, wind, UV index, sunrise & sunset).
- Powered by [Open-Meteo API](https://open-meteo.com/).

### Wikipedia
- Searches and summarizes Wikipedia topics.
- Extracts **keywords** (RAKE) and generates **summaries** (TextRank).
- Uses the [Wikipedia REST API](https://www.mediawiki.org/wiki/API:REST_API).

### Tech News (Hacker News)
- Retrieves the latest tech-related stories via [Hacker News Algolia API](https://hn.algolia.com/api).
- Performs a **sentiment score** analysis for each title.

### Currency Exchange (Frankfurter.app)
- Converts between major currencies and shows **historical exchange rates (7 days)**.
- Uses [Frankfurter.app](https://www.frankfurter.app/) — ✅ **no API key required**.

### NLP Intelligence
- Keyword extraction (RAKE)
- Summarization (TextRank)
- Heuristic sentiment analysis

---

## Architecture Overview
<p align="center">
  <img src="Architecture.PNG" alt="IntelliDash Overview" width="700">
</p>

---

## How to run it locally? 

### Create and activate a virtual environment
```bash

## How to run it in a Python environment?

1: git clone https://github.com/AlvaroG88/IntelliDash
2: cd IntelliDash
3: python -m venv .venv
4: . .venv/Scripts/Activate.ps1     # On Windows PowerShell
# or
4: source .venv/bin/activate        # On macOS / Linux
### Install dependencies
5: pip install -r requirements.txt

### Run the web application
6: streamlit run app.py
Then open http://localhost:8501 in your browser.

---

## How to run it in a Docker container?
```bash
1: git clone https://github.com/AlvaroG88/IntelliDash
2: cd IntelliDash
3: docker compose up --build

To stop the container:
docker compose down

---
## How to run tests?
1: pip install -r requirements-dev.txt
2: pytest tests/

## Testing
The project has a suite of tests to ensure the quality of the code. The tests are located in the `tests/` directory and are split into two files:
### `tests/test_nlp.py`
This file tests the Natural Language Processing functions in `intelligence/nlp.py`. It includes tests for:
- `tokenize`: Checks if the function correctly tokenizes a string.
- `sentences`: Checks if the function correctly splits a text into sentences.
- `rake_keywords`: Checks if the RAKE algorithm correctly extracts keywords.
- `textrank_summarize`: Checks if the TextRank algorithm correctly summarizes a text.
- `tiny_sentiment`: Checks if the sentiment analysis function correctly identifies positive, negative, and neutral sentiments.
### `tests/test_services.py`
This file tests the external service integrations in the `services/` directory. It uses `pytest-mock` to mock API calls and test the following functions:
- `forex.convert_currency`: Tests successful and failing currency conversions.
- `news.search_hn`: Tests successful and failing Hacker News searches.
- `weather.geocode_city`: Tests successful and failing city geocoding.
- `weather.get_weather`: Tests successful and failing weather data retrieval.
- `wiki.search_pages`: Tests successful and failing Wikipedia page searches.
- `wiki.get_summary`: Tests successful and failing Wikipedia summary retrieval.
---



