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

### Analytics & Logging
IntelliDash logs every query to a session-state dataset, which can be downloaded as a CSV. This dataset is useful for analyzing user behavior, performance, and data trends.

| Field | Type | Description |
| :--- | :--- | :--- |
| `timestamp` | String (ISO) | Exact time of the query. |
| `query` | String | The raw search text entered by the user. |
| `query_type` | String | Detected intent (e.g., `place`, `person`, `Abstract`). |
| `execution_time_sec` | Float | Time taken to aggregate all sources. |
| `place_name` | String | Resolved city name (if query is a place). |
| `country` | String | Country code of the resolved place. |
| `latitude` | Float | Latitude of the resolved place. |
| `longitude` | Float | Longitude of the resolved place. |
| `temperature_c` | Float | Current temperature in Celsius. |
| `windspeed_ms` | Float | Current wind speed in m/s. |
| `wind_direction` | Integer | Wind direction in degrees. |
| `is_day` | Integer | `1` if day, `0` if night. |
| `weather_code` | Integer | WMO weather code. |
| `daily_max_temp` | Float | Max daily temperature (°C). |
| `daily_min_temp` | Float | Min daily temperature (°C). |
| `daily_precip_sum` | Float | Total daily precipitation (mm). |
| `daily_uv_index` | Float | Max daily UV index. |
| `wiki_title` | String | Title of the top Wikipedia result. |
| `news_count` | Integer | Number of news stories found. |
| `avg_news_sentiment` | Float | Average sentiment score of news titles. |
| `positive_news_count` | Integer | Count of news stories with positive sentiment (>0). |
| `negative_news_count` | Integer | Count of news stories with negative sentiment (<0). |
| `total_news_points` | Integer | Sum of upvotes on Hacker News stories. |
| `total_news_comments` | Integer | Sum of comments on Hacker News stories. |
| `news_sources_count` | Integer | Count of unique domains in news results. |

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



