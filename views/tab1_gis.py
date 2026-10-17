# views/tab1_gis.py
import pandas as pd
import plotly.express as px
import streamlit as st


def render_tab1(
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
):
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
      st.markdown(
          f"""
            <div style="background-color:#ffffff; color:#111827; padding:12px 14px; border-radius:8px; border-left:4px solid #1E88E5; border:1px solid #e5e7eb; box-shadow:0 1px 3px rgba(0,0,0,0.05); margin-bottom:10px;">
                <div style="font-size:15px; font-weight:700; color:#111827; margin-bottom:6px;">{z_name.split(' (')[0]}</div>
                <div style="font-size:13px; color:#374151; font-weight:500;">
                    🌧️ Rain: <span style="background-color:#f3f4f6; color:#111827; padding:2px 8px; border-radius:4px; font-family:monospace; font-size:12px; border:1px solid #d1d5db; font-weight:700;">{zone_rain_inputs[z_name]} mm/h</span>
                    &nbsp;|&nbsp;
                    🌱 Soil: <span style="background-color:#f3f4f6; color:#111827; padding:2px 8px; border-radius:4px; font-family:monospace; font-size:12px; border:1px solid #d1d5db; font-weight:700;">{zone_soil_inputs[z_name]}% VWC</span>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )