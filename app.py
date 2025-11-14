import datetime as dt
from typing import List
import requests
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

from datetime import datetime
from services.weather import geocode_city, get_weather
from services.wiki import search_pages, get_summary
from services.news import search_hn
from services.forex import convert_currency, get_timeseries, get_common_currencies
from intelligence.nlp import rake_keywords, textrank_summarize, tiny_sentiment

st.set_page_config(page_title="IntelliDash", page_icon="🧠", layout="wide")

st.title("🧠 IntelliDash — Intelligent Multi-Source Dashboard")
st.caption("Open-source GUI pulling data from Open-Meteo, Wikipedia, Hacker News and exchangerate.host, with light NLP.")

with st.sidebar:
    st.header("Smart Search")
    q = st.text_input("Search a topic / place / ticker / concept", placeholder="e.g., Artificial Intelligence, Barcelona, inflation")
    st.caption("Runs across news + wiki + (geo) weather + FX, then summarizes.")
    run_all = st.button("Run Smart Search")

    st.markdown("---")
    st.subheader("Settings")
    max_news = st.slider("Max news results", 5, 30, 10, step=5)
    max_wiki = st.slider("Max wiki results", 3, 10, 5, step=1)
    max_sum_sent = st.slider("Summary sentences", 1, 6, 3, step=1)

def smart_aggregate(query: str, max_news: int, max_wiki: int) -> dict:
    out = {"news": [], "wiki": [], "weather": None, "fx": None, "geo": None, "errors": []}
    if not query:
        return out
    # Wiki
    try:
        wp = search_pages(query, limit=max_wiki)
        out["wiki"] = wp
    except Exception as e:
        out["errors"].append(f"wiki: {e}")
    # News
    try:
        hn = search_hn(query, hits_per_page=max_news)
        out["news"] = hn
    except Exception as e:
        out["errors"].append(f"news: {e}")
    # Geo/weather si parece ciudad
    try:
        g = geocode_city(query)
        if g:
            out["geo"] = g
            w = get_weather(g["latitude"], g["longitude"])
            out["weather"] = w
    except Exception as e:
        out["errors"].append(f"weather: {e}")
    # FX si parece par de divisas
    try:
        tokens = query.upper().split()
        pair = None
        if len(tokens) == 1 and len(tokens[0]) == 6:
            pair = (tokens[0][:3], tokens[0][3:])
        elif "TO" in tokens and len(tokens) >= 3:
            i = tokens.index("TO")
            pair = (tokens[i-1], tokens[i+1]) if i-1 >=0 and i+1 < len(tokens) else None
        if pair:
            conv = fx_convert(1.0, pair[0], pair[1])
            if conv:
                out["fx"] = conv
    except Exception as e:
        out["errors"].append(f"fx: {e}")
    return out

def section_wiki(query: str, max_wiki: int, max_sum_sent: int):
    st.subheader("📚 Wikipedia")
    pages = search_pages(query, limit=max_wiki)
    if not pages:
        st.info("No results.")
        return
    cols = st.columns(2)
    for i, p in enumerate(pages):
        title = p.get("title")
        with cols[i % 2]:
            with st.expander(f"{title}"):
                summ = get_summary(title)
                if not summ:
                    st.write("No summary available.")
                    continue
                extract = summ.get("extract", "")
                st.write(extract)
                if extract:
                    st.markdown("**Keywords**")
                    kws = rake_keywords(extract, top_k=8)
                    st.write(", ".join(k for k, _ in kws))
                    st.markdown("**Auto-Summary**")
                    sum_sents = textrank_summarize(extract, max_sentences=max_sum_sent)
                    st.write(" ".join(sum_sents))

def section_news(query: str, max_news: int):
    st.subheader("🗞️ Hacker News (Algolia)")
    hits = search_hn(query, hits_per_page=max_news)
    if not hits:
        st.info("No results.")
        return
    for h in hits:
        title = h.get("title")
        url = h.get("url") or h.get("story_url")
        txt = f"{title} — {url or ''}"
        st.markdown(f"- {txt}")
        if title:
            s = tiny_sentiment(title)
            st.caption(f"Sentiment score: {s:+.2f}")

def section_weather(query: str):
    st.subheader("⛅ Weather (Open-Meteo)")
    g = geocode_city(query)
    if not g:
        st.info("Enter a city name to fetch weather.")
        return

    st.caption(f"Location resolved: {g.get('name')}, {g.get('country_code')} (lat {g.get('latitude')}, lon {g.get('longitude')})")
    w = get_weather(g["latitude"], g["longitude"])
    if not w:
        st.warning("Could not load weather.")
        return

    # Datos actuales
    cur = w.get("current_weather", {})
    temp_c = cur.get("temperature")
    temp_f = temp_c * 9/5 + 32 if temp_c is not None else None

    # Datos diarios
    daily = w.get("daily", {})
    uv = None
    sunrise = None
    sunset = None
    if daily:
        uv_list = daily.get("uv_index_max")
        sr_list = daily.get("sunrise")
        ss_list = daily.get("sunset")
        if uv_list:
            uv = uv_list[0]
        if sr_list:
            sunrise = sr_list[0]
        if ss_list:
            sunset = ss_list[0]

    # Convertir y formatear las horas de amanecer y anochecer
    def format_time(iso_str: str):
        try:
            dt_obj = datetime.fromisoformat(iso_str)
            return dt_obj.strftime("%H:%M %Z")  # hora + zona horaria
        except Exception:
            return iso_str

    sunrise_fmt = format_time(sunrise) if sunrise else None
    sunset_fmt = format_time(sunset) if sunset else None

    # Métricas principales
    st.metric("Temperature (°C)", temp_c)
    st.metric("Temperature (°F)", f"{temp_f:.1f}" if temp_f is not None else "N/A")
    st.metric("Wind (m/s)", cur.get("windspeed"))
    st.metric("UV Index (max)", uv if uv is not None else "N/A")

    # Detalles de sol
    with st.expander("🌅 Sun Info"):
        if sunrise_fmt and sunset_fmt:
            st.write(f"**Sunrise:** {sunrise_fmt}")
            st.write(f"**Sunset:** {sunset_fmt}")
        else:
            st.write("No sunrise/sunset data available.")

    # Gráfica de temperatura
    hourly = w.get("hourly", {})
    if hourly:
        df = pd.DataFrame({
            "time": pd.to_datetime(hourly.get("time", [])),
            "temp_c": hourly.get("temperature_2m", [])
        }).set_index("time")
        st.line_chart(df)

def section_fx():
    st.subheader("💱 FX Converter)")

    currencies = get_common_currencies()

    c1, c2, c3 = st.columns(3)
    with c1:
        amount = st.number_input("Amount", min_value=0.0, value=100.0, step=1.0)
    with c2:
        base = st.selectbox("From currency", currencies, index=0)
    with c3:
        target = st.selectbox("To currency", currencies, index=1)

    if st.button("Convert"):
        js = convert_currency(amount, base, target)
        if not js["success"]:
            st.error(f"Conversion failed: {js.get('error', 'Unknown error')}")
            st.json(js.get("raw", {}))
            return

        st.success(f"{amount:.2f} {base} = {js['result']:.4f} {target}")
        if js.get("rate"):
            st.caption(f"Exchange rate: 1 {base} = {js['rate']:.4f} {target}")

    # Histórico
    st.markdown("### 📈 Exchange Rate (Last 7 Days)")
    df = get_timeseries(base, target, days=7)
    if df is not None and not df.empty:
        chart = (
           alt.Chart(df.reset_index())
           .mark_line(point=True, color="#4B9CD3")
           .encode(
               x=alt.X("date:T", title="Date"),
               y=alt.Y("rate:Q", title=f"Exchange Rate ({base} → {target})", scale=alt.Scale(zero=False)),
               tooltip=[
                   alt.Tooltip("date:T", title="Date"),
                   alt.Tooltip("rate:Q", title=f"Rate ({base}/{target})", format=".4f"),
               ],
           )
           .properties(title="📈 Exchange Rate (Last 7 Days)", width="container", height=300)
           .interactive()
          )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No historical data available.")


# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Smart Search", "Wikipedia", "News", "Weather", "FX Converter"])

with tab1:
    st.header("🔎 Smart Search (multi-source + summarize)")
    st.write("Enter a query in the sidebar and press **Run Smart Search**.")
    if run_all and q:
        res = smart_aggregate(q, max_news, max_wiki)
        if res["errors"]:
            st.warning("Some sources had errors: " + "; ".join(res["errors"]))
        if res["wiki"]:
            st.subheader("Top Wiki Page")
            top = res["wiki"][0]
            title = top.get("title")
            st.markdown(f"**{title}**")
            summ = get_summary(title) or {}
            extract = summ.get("extract", "")
            if extract:
                st.write(extract)
                st.markdown("**Auto-Summary**")
                st.write(" ".join(textrank_summarize(extract, max_sentences=max_sum_sent)))
        if res["news"]:
            st.subheader("News Highlights")
            for h in res["news"][:5]:
                title = h.get("title") or ""
                url = h.get("url") or h.get("story_url") or ""
                st.markdown(f"- {title} — {url}")
        if res["weather"] and res["geo"]:
            st.subheader("Weather Snapshot")
            cur = res["weather"].get("current_weather", {})
            st.caption(f"{res['geo'].get('name')}, {res['geo'].get('country_code')}")
            st.metric("Temp (°C)", cur.get("temperature"))
            st.metric("Wind (m/s)", cur.get("windspeed"))
        if res["fx"]:
            st.subheader("FX 1-unit Conversion")
            info = res["fx"]
            st.write(f"1 {info['query']['from']} = {info['result']:.4f} {info['query']['to']}")

with tab2:
    query = st.text_input("Search Wikipedia:", value="Artificial intelligence")
    section_wiki(query, max_wiki, max_sum_sent)

with tab3:
    query = st.text_input("Search Hacker News:", value="AI")
    section_news(query, max_news)

with tab4:
    city = st.text_input("City:", value="Barcelona")
    section_weather(city)

with tab5:
    section_fx()
