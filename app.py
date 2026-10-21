# app.py
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st

from config import CUSTOM_CSS, TOWNSHIP_ZONES
from services.ml_engine import predict_ml_flood_risk
from services.weather_api import fetch_live_weather_and_forecast
from views.tab1_gis import render_tab1
from views.tab2_telemetry_3d import render_tab2
from views.tab3_weather_ml import render_tab3
from views.tab4_roi_pdf import render_tab4
from views.tab5_citizen_alerts import render_tab5
from views.tab6_ai_assistant import render_tab6
from views.tab7_duty_roster import render_tab7

# Page Setup
st.set_page_config(
    page_title="HydroResilience IoT | SDP Engine",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session State Initializer
if "citizen_reports" not in st.session_state:
  st.session_state.citizen_reports = [
      {
          "id": "REP-101",
          "zone": "Elmina West",
          "category": "Clogged Street Drain",
          "desc": (
              "Heavy leaf debris and mud blocking curb inlet near Phase 1 park"
              " entry."
          ),
          "status": "In Progress",
          "time": "15 mins ago",
          "image": None,
      },
      {
          "id": "REP-102",
          "zone": "Elmina East",
          "category": "Localized Road Ponding",
          "desc": "Water accumulation along commercial row during heavy downpour.",
          "status": "In Progress",
          "time": "1 hour ago",
          "image": None,
      },
  ]

# Sidebar Controls
st.sidebar.image("https://img.icons8.com/color/96/water.png", width=64)
st.sidebar.title("SDP HydroResilience")
st.sidebar.caption("Enterprise IoT & Multi-Zone Engine")

selected_township = st.sidebar.selectbox(
    "Select Target Township", list(TOWNSHIP_ZONES.keys())
)
township_data = TOWNSHIP_ZONES[selected_township]

# Weather API Data Fetch
first_zone_coords = list(township_data["zones"].values())[0]
live_temp, live_rain, forecast_times, forecast_precip = (
    fetch_live_weather_and_forecast(
        first_zone_coords["lat"], first_zone_coords["lon"]
    )
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌧️ Micro-Climate Zone Rain Simulation")

zone_rain_inputs = {}
zone_soil_inputs = {}
for zone_name in township_data["zones"].keys():
  st.sidebar.markdown(f"**{zone_name.split(' (')[0]}**")
  z_rain = st.sidebar.slider(
      f"Rain (mm/h) - {zone_name[:12]}", 0.0, 60.0, 16.0, key=f"r_{zone_name}"
  )
  z_soil = st.sidebar.slider(
      f"Soil (% VWC) - {zone_name[:12]}", 10, 60, 22, key=f"s_{zone_name}"
  )
  zone_rain_inputs[zone_name] = z_rain
  zone_soil_inputs[zone_name] = z_soil

pond_level = st.sidebar.slider("Central Retention Pond Level (%)", 10, 100, 78)

# Calculate Spatial Inflow Runoff
total_hourly_runoff_m3 = 0.0
for zone_name, z_props in township_data["zones"].items():
  r_intensity = zone_rain_inputs[zone_name]
  c_coeff = z_props["runoff_coeff"]
  area = z_props["area_m2"]
  total_hourly_runoff_m3 += (r_intensity / 1000.0) * c_coeff * area

avg_soil_moisture = np.mean(list(zone_soil_inputs.values()))
sum_4h_forecast = sum(forecast_precip[:4])

ml_peak_level, ml_risk_class, ml_confidence, ml_risk_color = (
    predict_ml_flood_risk(
        pond_level, total_hourly_runoff_m3, avg_soil_moisture, sum_4h_forecast
    )
)

if pond_level > 80 and total_hourly_runoff_m3 > 1200:
  status_mode = "CRITICAL_DISCHARGE"
  status_msg = (
      f"⚠️ CRITICAL: PRE-DISCHARGE ACTUATED. Combined runoff"
      f" ({total_hourly_runoff_m3:,.0f} m³/h) exceeds safety thresholds."
  )
  status_color = "#FFEBEE"
  text_color = "#C62828"
elif total_hourly_runoff_m3 >= 200 and pond_level < 90:
  status_mode = "HARVESTING"
  status_msg = (
      f"🌧️ HARVESTING ACTIVE: Diverting {total_hourly_runoff_m3:,.0f} m³/h"
      " stormwater runoff into non-potable storage."
  )
  status_color = "#E3F2FD"
  text_color = "#1565C0"
elif avg_soil_moisture < 30:
  status_mode = "IRRIGATING"
  status_msg = (
      "🌱 SMART IRRIGATION ACTIVE: Supplying non-potable water to park root"
      " zones."
  )
  status_color = "#E8F5E9"
  text_color = "#2E7D32"
else:
  status_mode = "OPTIMAL"
  status_msg = "✅ SYSTEM OPTIMAL: Moisture balanced & pond capacity stable."
  status_color = "#F3E5F5"
  text_color = "#6A1B9A"

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab7, tab6 = st.tabs([
    "📍 Executive GIS Command",
    "⚡ Telemetry & 3D Basin View",
    "⛈️ Weather API & ML Forecast",
    "💰 Commercial ROI & ESG PDF",
    "📋 Citizen Portal & Emergency Copy-Alert",
    "👷 On-Duty Personnel Roster",
    "🤖 Hydro-AI Operator",
])

with tab1:
  render_tab1(
      selected_township,
      township_data,
      status_mode,
      status_msg,
      status_color,
      text_color,
      zone_rain_inputs,
      zone_soil_inputs,
      total_hourly_runoff_m3,
      live_temp,
  )

with tab2:
  render_tab2(
      pond_level,
      avg_soil_moisture,
      township_data,
      zone_rain_inputs,
      zone_soil_inputs,
      status_mode,
  )

# Construct forecast payload for Tab 3
ml_forecast_data = {
    "risk_curve": [
        ml_peak_level,
        min(100.0, ml_peak_level * 0.95),
        min(100.0, ml_peak_level * 0.85),
        min(100.0, ml_peak_level * 0.70),
        min(100.0, ml_peak_level * 0.50),
        30.0,
        20.0,
        15.0,
    ],
    "rain_curve": (
        forecast_precip[:8]
        if forecast_precip
        else [0, 2, 8, 25, 32, 18, 5, 1]
    ),
}

with tab3:
  render_tab3(
      selected_township,
      township_data,
      pond_level,
      avg_soil_moisture,
      ml_forecast_data,
  )

with tab4:
  park_size, annual_rm_saved, payback_years = render_tab4(
      selected_township,
      status_mode,
      status_msg,
      pond_level,
      ml_peak_level,
      ml_risk_class,
      avg_soil_moisture,
      total_hourly_runoff_m3,
  )

with tab5:
  render_tab5(
      selected_township,
      status_mode,
      pond_level,
      total_hourly_runoff_m3,
      township_data,
  )

with tab7:
  render_tab7(selected_township)

with tab6:
  render_tab6(
      selected_township,
      status_mode,
      total_hourly_runoff_m3,
      park_size,
      annual_rm_saved,
      payback_years,
      ml_peak_level,
      ml_risk_class,
      ml_confidence,
  )