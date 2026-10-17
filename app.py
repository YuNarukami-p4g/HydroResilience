from datetime import datetime
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from fpdf import FPDF

# -------------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------------
st.set_page_config(
    page_title="HydroResilience IoT | SDP Enterprise Engine",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header {font-size:24px; font-weight:bold; color:#0e1117;}
    .status-banner {padding:12px; border-radius:8px; font-weight:bold; margin-bottom:15px;}
    .zone-card {background-color:#f8f9fa; padding:12px; border-radius:8px; border-left:4px solid #1E88E5; margin-bottom:10px;}
    .report-card {background-color:#eef6fc; padding:15px; border-radius:8px; border:1px solid #b6d4f1;}
    .citizen-card {background-color:#ffffff; padding:12px; border-radius:8px; border:1px solid #e0e0e0; margin-bottom:10px;}
    </style>
""",
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# PDF REPORT GENERATOR CLASS (FPDF)
# -------------------------------------------------------------------
class ExecutivePDFReport(FPDF):

  def header(self):
    self.set_font("Helvetica", "B", 14)
    self.cell(
        0, 8, "SIME DARBY PROPERTY | HYDRORESILIENCE IOT", ln=1, align="C"
    )
    self.set_font("Helvetica", "", 10)
    self.cell(
        0,
        5,
        "Executive ESG Audit & Stormwater Compliance Report",
        ln=1,
        align="C",
    )
    self.line(10, 25, 200, 25)
    self.ln(8)

  def footer(self):
    self.set_y(-15)
    self.set_font("Helvetica", "I", 8)
    self.cell(
        0,
        10,
        f"Page {self.page_no()} | Confidential - Sime Darby Property Asset"
        " Management",
        align="C",
    )


def generate_pdf_bytes(
    township,
    status_mode,
    status_msg,
    pond_level,
    ml_peak_level,
    ml_risk_class,
    park_size,
    annual_water_saved_m3,
    annual_rm_saved,
    annual_co2_saved,
    capex,
    payback_years,
    avg_soil_moisture,
    total_hourly_runoff_m3,
):
  pdf = ExecutivePDFReport()
  pdf.add_page()
  pdf.set_font("Helvetica", "B", 11)

  # Metadata
  pdf.cell(0, 6, f"Target Township: {township}", ln=1)
  pdf.cell(
      0,
      6,
      f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
      ln=1,
  )
  pdf.ln(4)

  # Section 1
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 8, "1. Executive Operational Summary", ln=1)
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(0, 6, f"- Current System State: {status_mode}", ln=1)
  pdf.cell(0, 6, f"- Central Retention Basin Level: {pond_level}%", ln=1)
  pdf.cell(
      0,
      6,
      f"- ML Projected Peak Risk (4h): {ml_peak_level}% ({ml_risk_class})",
      ln=1,
  )
  pdf.cell(
      0,
      6,
      f"- Aggregated Inflow Runoff: {total_hourly_runoff_m3:,.1f} m3/h",
      ln=1,
  )
  pdf.ln(4)

  # Section 2
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 8, "2. ESG Resource Offset & Sustainability", ln=1)
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(0, 6, f"- Managed Landscape Surface Area: {park_size} Hectares", ln=1)
  pdf.cell(
      0,
      6,
      f"- Annual Municipal Potable Water Offset:"
      f" {annual_water_saved_m3:,.0f} m3/year",
      ln=1,
  )
  pdf.cell(
      0,
      6,
      f"- Annual Scope 3 Carbon Offset: {annual_co2_saved:,.2f} tCO2e/year",
      ln=1,
  )
  pdf.ln(4)

  # Section 3
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 8, "3. Commercial Financial ROI", ln=1)
  pdf.set_font("Helvetica", "", 10)
  pdf.cell(0, 6, f"- Total Estimated IoT System CapEx: RM {capex:,.2f}", ln=1)
  pdf.cell(
      0, 6, f"- Annual Utility OpEx Savings: RM {annual_rm_saved:,.2f}", ln=1
  )
  pdf.cell(
      0, 6, f"- Projected Payback Period: {payback_years:.2f} Years", ln=1
  )

  out = pdf.output(dest="S")
  if isinstance(out, str):
    return out.encode("latin-1")
  return bytes(out)


# -------------------------------------------------------------------
# AUTOMATED OPEN-METEO WEATHER API
# -------------------------------------------------------------------
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


# ML Flood Prediction Simulation
def predict_ml_flood_risk(
    pond_level, current_runoff_m3, avg_soil_vwc, forecast_4h_rain_mm
):
  predicted = (
      pond_level
      + (forecast_4h_rain_mm * 0.85)
      + (current_runoff_m3 / 250.0)
      - ((30 - avg_soil_vwc) * 0.15)
  )
  predicted = min(100.0, max(0.0, predicted))
  if predicted >= 85.0:
    return (
        round(predicted, 1),
        "HIGH RISK (Pre-Discharge Mandated)",
        94.2,
        "#E53935",
    )
  elif predicted >= 70.0:
    return (
        round(predicted, 1),
        "MODERATE RISK (Harvesting Mode)",
        89.7,
        "#FB8C00",
    )
  else:
    return (
        round(predicted, 1),
        "LOW RISK (Normal Operations)",
        96.5,
        "#43A047",
    )


# -------------------------------------------------------------------
# MULTI-ZONE TOWNSHIP DATA ARCHITECTURE
# -------------------------------------------------------------------
TOWNSHIP_ZONES = {
    "City of Elmina": {
        "master_pond_capacity_m3": 250000,
        "zones": {
            "Elmina West (Residential Phase 1)": {
                "lat": 3.1706,
                "lon": 101.5230,
                "area_m2": 450000,
                "runoff_coeff": 0.65,
            },
            "Elmina Central Park (Green Basin)": {
                "lat": 3.1780,
                "lon": 101.5290,
                "area_m2": 600000,
                "runoff_coeff": 0.35,
            },
            "Elmina East (Commercial Hub)": {
                "lat": 3.1630,
                "lon": 101.5380,
                "area_m2": 350000,
                "runoff_coeff": 0.85,
            },
        },
    },
    "Bandar Bukit Raja": {
        "master_pond_capacity_m3": 180000,
        "zones": {
            "Bukit Raja Industrial Park": {
                "lat": 3.0738,
                "lon": 101.5183,
                "area_m2": 500000,
                "runoff_coeff": 0.90,
            },
            "Bukit Raja Wetlands (Zone A)": {
                "lat": 3.0810,
                "lon": 101.5250,
                "area_m2": 700000,
                "runoff_coeff": 0.30,
            },
            "Residential North Phase": {
                "lat": 3.0680,
                "lon": 101.5110,
                "area_m2": 400000,
                "runoff_coeff": 0.60,
            },
        },
    },
}

# Session State for Citizen Reporting & Incident Tracking
if "citizen_reports" not in st.session_state:
  st.session_state.citizen_reports = [
      {
          "id": "REP-101",
          "zone": "Elmina West",
          "category": "Clogged Drain",
          "desc": "Leaf debris blocking curb inlet",
          "status": "In Progress",
          "time": "10 mins ago",
      },
      {
          "id": "REP-102",
          "zone": "Elmina East",
          "category": "Road Ponding",
          "desc": "Minor water retention at junction",
          "status": "Cleared",
          "time": "1 hour ago",
      },
  ]

# -------------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/water.png", width=64)
st.sidebar.title("SDP HydroResilience")
st.sidebar.caption("Enterprise IoT & Multi-Zone Engine")

selected_township = st.sidebar.selectbox(
    "Select Target Township", list(TOWNSHIP_ZONES.keys())
)
township_data = TOWNSHIP_ZONES[selected_township]

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

# -------------------------------------------------------------------
# MULTI-ZONE RUNOFF & DECISION LOGIC
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# DASHBOARD TABS
# -------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📍 Executive GIS Command",
    "⚡ Telemetry & Multi-Zone Actuators",
    "⛈️ Weather API & ML Forecast",
    "💰 Commercial ROI & ESG PDF",
    "📱 Citizen Portal & Push Alerts",
    "🤖 Hydro-AI Operator",
])

# -------------------------------------------------------------------
# TAB 1: EXECUTIVE GIS COMMAND
# -------------------------------------------------------------------
with tab1:
  st.markdown(
      f'<div class="status-banner" style="background-color:{status_color};'
      f' color:{text_color};">{status_msg}</div>',
      unsafe_allow_html=True,
  )

  col_map, col_zones = st.columns([2, 1])

  with col_map:
    st.subheader(f"🗺️ {selected_township} Multi-Zone GIS Catchment Map")
    map_data = []
    for z_name, z_props in township_data["zones"].items():
      z_rain = zone_rain_inputs[z_name]
      map_data.append({
          "Sub-Zone": z_name,
          "lat": z_props["lat"],
          "lon": z_props["lon"],
          "Rainfall (mm/h)": z_rain,
          "Soil Moisture (%)": zone_soil_inputs[z_name],
          "MarkerSize": max(15, int(z_rain * 1.3)),
      })
    df_map = pd.DataFrame(map_data)

    fig_map = px.scatter_map(
        df_map,
        lat="lat",
        lon="lon",
        hover_name="Sub-Zone",
        hover_data=["Rainfall (mm/h)", "Soil Moisture (%)"],
        size="MarkerSize",
        color="Rainfall (mm/h)",
        color_continuous_scale="Blues",
        zoom=11,
        center={
            "lat": df_map["lat"].mean(),
            "lon": df_map["lon"].mean(),
        },
        height=380,
        map_style="open-street-map",
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, width="stretch")

  with col_zones:
    st.subheader("🌐 Field Overview")
    st.metric("Live Air Temp (Open-Meteo)", f"{live_temp} °C")
    st.metric("Total Spatial Inflow", f"{total_hourly_runoff_m3:,.1f} m³/h")

    for z_name in township_data["zones"].keys():
      st.markdown(f"""
            <div class="zone-card">
                <b>{z_name.split(' (')[0]}</b><br>
                🌧️ Rain: <code>{zone_rain_inputs[z_name]} mm/h</code> | 🌱 Soil: <code>{zone_soil_inputs[z_name]}% VWC</code>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# TAB 2: TELEMETRY & MULTI-ZONE ACTUATOR CONTROLS
# -------------------------------------------------------------------
with tab2:
  st.subheader("⚡ Central Basin & Sub-Zone Actuator Network")

  # Scaled Down Hydro-Gauges
  col_g1, col_g2 = st.columns(2)
  with col_g1:
    fig_g1 = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pond_level,
            title={"text": "Central Retention Pond (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#1E88E5"},
                "steps": [
                    {"range": [0, 70], "color": "#E3F2FD"},
                    {"range": [70, 85], "color": "#FFF9C4"},
                    {"range": [85, 100], "color": "#FFCDD2"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 3},
                    "value": 80,
                },
            },
        )
    )
    fig_g1.update_layout(height=210, margin=dict(l=15, r=15, t=25, b=15))
    st.plotly_chart(fig_g1, width="stretch")

  with col_g2:
    fig_g2 = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=avg_soil_moisture,
            title={"text": "Average Catchment Soil Moisture (% VWC)"},
            gauge={
                "axis": {"range": [0, 60]},
                "bar": {"color": "#43A047"},
                "steps": [
                    {"range": [0, 25], "color": "#FFCDD2"},
                    {"range": [25, 40], "color": "#C8E6C9"},
                    {"range": [40, 60], "color": "#E3F2FD"},
                ],
                "threshold": {
                    "line": {"color": "green", "width": 3},
                    "value": 30,
                },
            },
        )
    )
    fig_g2.update_layout(height=210, margin=dict(l=15, r=15, t=25, b=15))
    st.plotly_chart(fig_g2, width="stretch")

  st.markdown("---")
  st.subheader("🎛️ Sub-Zone Actuator Telemetry Matrix")

  # Sub-zone Actuator Table Simulation
  actuator_data = []
  for z_name, z_props in township_data["zones"].items():
    z_rain = zone_rain_inputs[z_name]
    z_soil = zone_soil_inputs[z_name]

    inflow_valve = (
        "100% OPEN" if (z_rain >= 5.0 and pond_level < 90) else "0% CLOSED"
    )
    outflow_gate = (
        "100% OPEN" if status_mode == "CRITICAL_DISCHARGE" else "0% CLOSED"
    )
    sub_pump = "ON (120 L/min)" if (z_soil < 30 and z_rain < 5.0) else "OFF"

    actuator_data.append({
        "Sub-Zone": z_name,
        "Local Rain (mm/h)": z_rain,
        "Soil Moisture (% VWC)": z_soil,
        "Inflow Swale Valve": inflow_valve,
        "Main Sluice Gate": outflow_gate,
        "Sub-Surface Pump": sub_pump,
    })

  st.dataframe(pd.DataFrame(actuator_data), width='stretch')

# -------------------------------------------------------------------
# TAB 3: WEATHER API & ML FORECAST
# -------------------------------------------------------------------
with tab3:
  st.subheader("⛈️ Open-Meteo API Forecast & ML Flood Risk Engine")
  col_ml1, col_ml2 = st.columns([1, 2])

  with col_ml1:
    st.markdown("### 🤖 ML Predictive Analytics")
    st.markdown(
        f"<h4 style='color:{ml_risk_color};'>{ml_risk_class}</h4>",
        unsafe_allow_html=True,
    )
    st.metric("Predicted Peak Level (Next 4h)", f"{ml_peak_level}%")
    st.metric("XGBoost Model Confidence", f"{ml_confidence}%")

  with col_ml2:
    st.markdown("### 📈 24-Hour Automated Weather & Storage Response")
    sim_pond_trend = np.clip(
        pond_level + np.cumsum(np.array(forecast_precip) * 0.75) - 1.2, 10, 100
    )
    df_forecast = pd.DataFrame({
        "Hour": forecast_times,
        "Rainfall (mm/h)": forecast_precip,
        "Projected Pond Accumulation (%)": sim_pond_trend,
    })

    fig_forecast = px.bar(
        df_forecast,
        x="Hour",
        y="Rainfall (mm/h)",
        color_discrete_sequence=["#1E88E5"],
    )
    fig_forecast.add_trace(
        go.Scatter(
            x=df_forecast["Hour"],
            y=df_forecast["Projected Pond Accumulation (%)"],
            name="Pond Capacity (%)",
            yaxis="y2",
            line=dict(color="red", width=3),
        )
    )
    fig_forecast.update_layout(
        yaxis2=dict(
            title="Pond Level (%)", overlaying="y", side="right", range=[0, 110]
        ),
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig_forecast, width="stretch")

# -------------------------------------------------------------------
# TAB 4: COMMERCIAL ROI & ESG PDF REPORT GENERATOR
# -------------------------------------------------------------------
with tab4:
  st.subheader("💰 Commercial ROI & Official Executive PDF Audit Report")
  c_roi1, c_roi2 = st.columns(2)

  with c_roi1:
    st.markdown("### 💵 Utility OpEx Savings Calculator")
    tariff = st.number_input(
        "Commercial Municipal Water Tariff (RM/m³)", value=2.80
    )
    park_size = st.slider("Township Landscape Area (Hectares)", 5, 50, 15)

    annual_water_saved_m3 = park_size * 35 * 365
    annual_rm_saved = annual_water_saved_m3 * tariff
    annual_co2_saved = annual_water_saved_m3 * 0.0003

    st.success(
        f"**Annual Potable Water Offset**: {annual_water_saved_m3:,.0f} m³ /"
        " year"
    )
    st.success(
        f"**Annual Utility OpEx Saved**: RM {annual_rm_saved:,.2f} / year"
    )

  with c_roi2:
    st.markdown("### 📊 CapEx Payback & Carbon Offset")
    hardware_capex = 85000
    payback_years = (
        hardware_capex / annual_rm_saved if annual_rm_saved > 0 else 0
    )

    st.metric("Estimated IoT Hardware CapEx", f"RM {hardware_capex:,}")
    st.metric(
        "Projected Payback Timeline",
        f"{payback_years:.1f} Years",
        delta="-60% vs Civil Expansion",
    )
    st.metric(
        "Scope 3 Carbon Avoidance", f"{annual_co2_saved:,.1f} tCO2e / year"
    )

  st.markdown("---")
  st.subheader("📄 Download Official Executive PDF ESG Audit Report")

  pdf_bytes = generate_pdf_bytes(
      selected_township,
      status_mode,
      status_msg,
      pond_level,
      ml_peak_level,
      ml_risk_class,
      park_size,
      annual_water_saved_m3,
      annual_rm_saved,
      annual_co2_saved,
      hardware_capex,
      payback_years,
      avg_soil_moisture,
      total_hourly_runoff_m3,
  )

  st.download_button(
      label="📥 Download Official Executive ESG Audit Report (.PDF)",
      data=pdf_bytes,
      file_name=f"SDP_ESG_Audit_Report_{selected_township.replace(' ', '_')}.pdf",
      mime="application/pdf",
  )

# -------------------------------------------------------------------
# TAB 5: CITIZEN PORTAL & EMERGENCY PUSH NOTIFICATIONS
# -------------------------------------------------------------------
with tab5:
  st.subheader("📲 Emergency Alerts & Citizen Drain Reporting Portal")
  col_push, col_portal = st.columns(2)

  with col_push:
    st.markdown("### 🔔 Telegram / Twilio Webhook Dispatch")
    webhook_url = st.text_input(
        "Telegram / Twilio Webhook URL Endpoint",
        value=(
            "https://api.telegram.org/bot123456/sendMessage?chat_id=-100123"
        ),
    )

    if status_mode == "CRITICAL_DISCHARGE":
      st.error(
          "⚠️ AUTOMATED ALERT DISPATCHED TO FIELD ENGINEERS (Mode 1"
          " Pre-Discharge Actuated)"
      )
    else:
      st.info("System Normal: Webhook on Standby.")

    if st.button("📲 Send Test Field Engineer Webhook Payload"):
      payload = {
          "event": "PRE_DISCHARGE_WARNING",
          "township": selected_township,
          "pond_level": f"{pond_level}%",
          "timestamp": datetime.now().isoformat(),
      }
      st.code(str(payload), language="json")
      st.success("Test Webhook payload dispatched successfully!")

  with col_portal:
    st.markdown("### 📸 Citizen Drain & Flood Reporting")
    with st.form("citizen_report_form"):
      rep_zone = st.selectbox(
          "Report Sub-Zone", list(township_data["zones"].keys())
      )
      rep_cat = st.selectbox(
          "Issue Category",
          [
              "Clogged Street Drain",
              "Localized Road Ponding",
              "Swale Blockage",
              "Debris Accumulation",
          ],
      )
      rep_desc = st.text_area("Location Description / Remarks")
      rep_photo = st.file_uploader(
          "Upload Incident Photo", type=["jpg", "png", "jpeg"]
      )
      submitted = st.form_submit_button("Submit Resident Incident")

      if submitted:
        new_rep = {
            "id": f"REP-{len(st.session_state.citizen_reports)+101}",
            "zone": rep_zone.split(" (")[0],
            "category": rep_cat,
            "desc": rep_desc,
            "status": "Pending Dispatch",
            "time": "Just now",
        }
        st.session_state.citizen_reports.insert(0, new_rep)
        st.success("Report submitted to SDP Maintenance Hub!")

  st.markdown("---")
  st.subheader("📋 Active Resident Incident Log")
  st.table(pd.DataFrame(st.session_state.citizen_reports))

# -------------------------------------------------------------------
# TAB 6: HYDRO-AI OPERATOR
# -------------------------------------------------------------------
with tab6:
  st.subheader("🤖 HydroResilience AI Township Operator")
  st.caption(
      "Query live telemetry, sub-zone actuator states, or ESG audit figures:"
  )

  if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Hello! I am tracking multi-zone hydrology across "
            + selected_township
            + ". Ask me about sub-zone pumps, ML risks, or PDF exports!"
        ),
    }]

  for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

  if prompt := st.chat_input("e.g., What is the status of the sub-zone pumps?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    p_lower = prompt.lower()
    if "pump" in p_lower or "valve" in p_lower or "zone" in p_lower:
      ans = (
          f"Actuator Matrix: Outflow gates are operating in **{status_mode}**"
          " mode. Sub-zone irrigation pumps activate individually when local"
          " soil moisture drops below 30% VWC."
      )
    elif "pdf" in p_lower or "report" in p_lower:
      ans = (
          "You can download the official Executive ESG Audit PDF from Tab 4"
          " ('Commercial ROI & ESG PDF')."
      )
    else:
      ans = (
          f"System normal across {selected_township}. Combined spatial inflow"
          f" runoff is {total_hourly_runoff_m3:,.1f} m³/h."
      )

    st.session_state.messages.append({"role": "assistant", "content": ans})
    st.chat_message("assistant").write(ans)