# views/tab6_ai_assistant.py
import streamlit as st


def generate_smart_response(
    prompt,
    selected_township,
    status_mode,
    total_hourly_runoff_m3,
    park_size,
    annual_rm_saved,
    payback_years,
    ml_peak_level,
    ml_risk_class,
    ml_confidence,
    pond_level,
    avg_soil_moisture,
):
  """Domain-specific heuristic intelligence engine for HydroResilience copilot."""
  p = prompt.lower()

  # 1. FLOOD RISK, ML FORECASTING & CLOUDBURST
  if any(k in p for k in ["risk", "ml", "forecast", "predict", "flood", "peak", "rain", "storm"]):
    return (
        f"### ⛈️ Flood Risk Analysis for **{selected_township}**\n\n"
        f"* **Projected Peak Risk**: **{ml_peak_level:.1f}%** ({ml_risk_class})\n"
        f"* **Model Confidence**: **{ml_confidence}%** (XGBoost v2.1)\n"
        f"* **Current Inflow Runoff**: **{total_hourly_runoff_m3:,.1f} m³/h**\n"
        f"* **Active Mode**: `{status_mode}`\n\n"
        f"**Operational Protocol**: "
        + (
            "🚨 **Pre-Discharge Required**: Sluice gates are set to open automatically to create retention buffer volume."
            if ml_peak_level >= 60
            else "🟢 **Safe Capacity**: Basin headroom is sufficient to absorb forecasted precipitation."
        )
    )

  # 2. ACTUATOR CONTROL, HYSTERESIS & SENSOR SAFETY
  elif any(k in p for k in ["hysteresis", "actuator", "control", "pump", "gate", "valve", "sensor", "fault", "lockout"]):
    return (
        f"### 🎛️ Actuator & Hysteresis Control Logic\n\n"
        f"HydroResilience enforces explicit dual-threshold bounds to protect hardware:\n\n"
        f"1. **Irrigation Hysteresis**:\n"
        f"   * **Activation Trigger**: Soil moisture drops below **25% VWC** and pond capacity $> 15\%$.\n"
        f"   * **Deactivation Trigger**: Soil moisture reaches **40% VWC** upper threshold.\n"
        f"2. **Safety Dry-Run Lockout**: Pumps automatically lock out when central retention depth drops to $\\le 15\%$.\n"
        f"3. **Pre-Discharge Mode**: Triggers when retention capacity exceeds **80%** and runoff $> 1,200\\text m^3/\\text h$.\n"
        f"4. **Fail-Safe Sensor Fault**: Disconnected or `NaN` feeds force all valves into closed standby mode."
    )

  # 3. FINANCIAL ROI, CAPEX & ESG AUDIT
  elif any(k in p for k in ["save", "cost", "roi", "esg", "money", "payback", "financial", "tariff", "carbon"]):
    carbon_offset_t = (annual_rm_saved / 2.80) * 0.0004  # Proxy Scope 3 calculation
    return (
        f"### 💰 Commercial ROI & ESG Impact Summary\n\n"
        f"* **Target Landscape Area**: **{park_size} hectares** ({selected_township})\n"
        f"* **Annual Utility OpEx Savings**: **RM {annual_rm_saved:,.2f} / year**\n"
        f"* **CapEx Amortization Payback**: **{payback_years:.1f} years**\n"
        f"* **Estimated Scope 3 Avoidance**: **~{carbon_offset_t:.2f} tCO₂e / year**\n\n"
        f"📄 You can download the complete executive board-ready audit report in **Tab 4 ('Commercial ROI & ESG PDF')**."
    )

  # 4. COMPLIANCE, STANDARDS & REGULATIONS
  elif any(k in p for k in ["standard", "msma", "iso", "did", "jps", "regulation", "sdg"]):
    return (
        f"### 📜 Engineering Standards & Compliance Remarks\n\n"
        f"* **🇲🇾 MSMA 2nd Edition (DID / JPS Malaysia)**: Complies with *Manual Saliran Mesra Alam* for On-Site Detention (OSD) and retention attenuation limits (5-yr to 100-yr ARI).\n"
        f"* **🌍 ISO 14001:2015 & ISO 31000**: Adheres to Environmental Management Systems and climate adaptation risk management protocols.\n"
        f"* **🌱 UN SDGs**: Direct alignment with **SDG 11** (Sustainable Cities) and **SDG 13** (Climate Action)."
    )

  # 5. CITIZEN PORTAL, FIELD DISPATCH & WHATSAPP
  elif any(k in p for k in ["citizen", "report", "whatsapp", "alert", "dispatch", "incident", "roster", "engineer"]):
    return (
        f"### 📱 Citizen Incident & Field Operations\n\n"
        f"* **Resident Photo Portal**: Residents submit flood/drainage photos in **Tab 5**. Status transitions from *In Progress* to *Resolved* in real time.\n"
        f"* **Emergency Payload Dispatch**: 1-click formatted clipboard payload contains live coordinates, runoff rate ({total_hourly_runoff_m3:,.0f} m³/h), and on-duty personnel info.\n"
        f"* **Shift Roster**: View active field engineers and contact cards in **Tab 7**."
    )

  # 6. HYDRAULIC FORMULAS & CALCULATION METHODOLOGY
  elif any(k in p for k in ["formula", "math", "rational", "coefficient", "calc", "runoff", "q="]):
    return (
        f"### 📐 Hydraulic Catchment Calculation Methodology\n\n"
        f"Spatial inflow runoff ($Q$) across sub-zones is calculated using the **Rational Method**:\n\n"
        f"$$Q = \\frac C \\cdot I \\cdot A {360}$$\n\n"
        f"* **$Q$**: Peak runoff rate (m³/s)\n"
        f"* **$C$**: Runoff coefficient (e.g., $0.85$ urban impervious vs. $0.30$ green parkland)\n"
        f"* **$I$**: Rainfall intensity (mm/h from live Open-Meteo API or simulation slider)\n"
        f"* **$A$**: Catchment surface area (hectares)"
    )

  # 7. 3D BASIN & TELEMETRY
  elif any(k in p for k in ["3d", "pond", "basin", "terrain", "gauge", "telemetry"]):
    return (
        f"### 🏔️ 3D Basin & Real-Time Telemetry\n\n"
        f"* **Current Pond Storage Depth**: **{pond_level}%**\n"
        f"* **Catchment Avg Soil Moisture**: **{avg_soil_moisture:.1f}% VWC**\n"
        f"* **3D Geometry Rendering**: Tab 2 displays a meshgrid surface model $(Z = (X^2 + Y^2) \\cdot 0.25)$ dynamically overlaid with the actual water elevation."
    )

  # 8. FALLBACK CONTEXTUAL SUMMARY
  else:
    return (
        f"### 🌊 HydroResilience Status Assistant ({selected_township})\n\n"
        f"Current operational snapshot:\n"
        f"* **System Status**: `{status_mode}`\n"
        f"* **Spatial Inflow Runoff**: **{total_hourly_runoff_m3:,.1f} m³/h**\n"
        f"* **Pond Storage Level**: **{pond_level}%**\n"
        f"* **Avg Catchment Soil**: **{avg_soil_moisture:.1f}% VWC**\n"
        f"* **4h Peak Risk Forecast**: **{ml_peak_level:.1f}%** ({ml_risk_class})\n\n"
        f"💡 *Try asking me about hysteresis thresholds, MSMA compliance, WhatsApp dispatch, ESG savings, or hydraulic formulas!*"
    )


def render_tab6(
    selected_township,
    status_mode,
    total_hourly_runoff_m3,
    park_size,
    annual_rm_saved,
    payback_years,
    ml_peak_level,
    ml_risk_class,
    ml_confidence,
    pond_level=78,
    avg_soil_moisture=22,
):
  st.subheader("🤖 Hydro-AI Operator Assistant")
  st.caption(
      f"Context-aware copilot monitoring **{selected_township}** telemetry,"
      " ML forecasts, and ESG compliance."
  )

  # Top Bar Controls
  col_info, col_clear = st.columns([4, 1])
  with col_clear:
    if st.button("🗑️ Clear Chat", width="stretch"):
      st.session_state.messages = []
      st.rerun()

  # Session State Initializer
  if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            f"Greetings! I am the Hydro-AI Copilot for **{selected_township}**."
            f" Current system mode is `{status_mode}` with a total runoff of"
            f" **{total_hourly_runoff_m3:,.1f} m³/h**.\n\nHow can I assist"
            " your operational team today?"
        ),
    }]

  # Display Existing Chat History
  for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

  # Quick Suggestion Pills
  st.markdown("#### 💡 Quick Operator Queries:")
  col_p1, col_p2, col_p3, col_p4 = st.columns(4)

  clicked_prompt = None
  if col_p1.button("⛈️ What's our flood risk?", width="stretch"):
    clicked_prompt = "What is our current flood risk and ML prediction?"
  if col_p2.button("🎛️ Explain pump logic", width="stretch"):
    clicked_prompt = "Explain actuator hysteresis and low tank lockout rules."
  if col_p3.button("💰 Calculate ESG ROI", width="stretch"):
    clicked_prompt = "What are the financial savings and ESG payback metrics?"
  if col_p4.button("📜 Engineering Standards", width="stretch"):
    clicked_prompt = "Which MSMA and ISO standards does this system meet?"

  # Handle User Input (either typing or clicking a pill)
  user_input = st.chat_input(
      "Ask about telemetry, actuators, MSMA standards, or ESG PDF..."
  )
  final_prompt = clicked_prompt if clicked_prompt else user_input

  if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    st.chat_message("user").write(final_prompt)

    response = generate_smart_response(
        final_prompt,
        selected_township,
        status_mode,
        total_hourly_runoff_m3,
        park_size,
        annual_rm_saved,
        payback_years,
        ml_peak_level,
        ml_risk_class,
        ml_confidence,
        pond_level,
        avg_soil_moisture,
    )

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)