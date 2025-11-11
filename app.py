import datetime as dt
from typing import List
import requests
import pandas as pd
import numpy as np
import streamlit as st

from services.weather import geocode_city, get_weather
from services.wiki import search_pages, get_summary
from services.news import search_hn
from services.forex import convert as fx_convert, timeseries as fx_timeseries
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
    cur = w.get("current_weather", {})
    st.metric("Temperature (°C)", cur.get("temperature"))
    st.metric("Wind (m/s)", cur.get("windspeed"))
    st.metric("Weather Code", cur.get("weathercode"))
    hourly = w.get("hourly", {})
    if hourly:
        df = pd.DataFrame({"time": pd.to_datetime(hourly.get("time", [])),
                           "temp_c": hourly.get("temperature_2m", [])})
        df = df.set_index("time")
        st.line_chart(df)

def section_fx():
    st.subheader("💱 FX Converter (exchangerate.host)")
    c1, c2, c3 = st.columns(3)
    with c1:
        amt = st.number_input("Amount", value=100.0, min_value=0.0, step=1.0)
    with c2:
        base = st.text_input("From", value="EUR", max_chars=3)
    with c3:
        target = st.text_input("To", value="USD", max_chars=3)
    if st.button("Convert"):
        js = fx_convert(amt, base, target)
        if not js:
            st.error("Conversion failed.")
        else:
            st.success(f"{amt} {base.upper()} = {js['result']:.4f} {target.upper()}")
    st.markdown("**History (last 7 days)**")
    end = dt.date.today()
    start = end - dt.timedelta(days=7)
    ts = fx_timeseries(base, target, start.isoformat(), end.isoformat())
    if ts and ts.get("rates"):
        rates = ts["rates"]
        dates = sorted(rates.keys())
        values = [rates[d][target.upper()] for d in dates]
        df = pd.DataFrame({"date": pd.to_datetime(dates), "rate": values}).set_index("date")
        st.line_chart(df)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Smart Search", "Wikipedia", "News", "Weather & FX"])

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
    st.markdown("---")
    section_fx()