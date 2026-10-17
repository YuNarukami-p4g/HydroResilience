# views/tab4_roi_pdf.py
import streamlit as st
from services.pdf_generator import generate_pdf_bytes


def render_tab4(
    selected_township,
    status_mode,
    status_msg,
    pond_level,
    ml_peak_level,
    ml_risk_class,
    avg_soil_moisture,
    total_hourly_runoff_m3,
):
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

  return park_size, annual_rm_saved, payback_years