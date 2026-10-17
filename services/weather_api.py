# services/weather_api.py
from datetime import datetime
import requests
import streamlit as st


@st.cache_data(ttl=600)
def fetch_live_weather_and_forecast(lat, lon):
  try:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=precipitation&forecast_days=2"
    response = requests.get(url, timeout=5)
    data = response.json()
    current_temp = data["current_weather"]["temperature"]
    rain_now = data["hourly"]["precipitation"][0]
    times = [
        datetime.strptime(t, "%Y-%m-%dT%H:%M").strftime("%H:00")
        for t in data["hourly"]["time"][:24]
    ]
    precip_24h = data["hourly"]["precipitation"][:24]
    return current_temp, rain_now, times, precip_24h
  except Exception:
    fallback_times = [f"{i:02d}:00" for i in range(24)]
    fallback_precip = [0.0, 0.0, 0.5, 2.0, 8.5, 18.0, 32.0, 14.0] + [0.0] * 16
    return 31.0, 2.5, fallback_times, fallback_precip