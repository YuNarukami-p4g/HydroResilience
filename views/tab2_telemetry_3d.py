# views/tab2_telemetry_3d.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_tab2(
    pond_level,
    avg_soil_moisture,
    township_data,
    zone_rain_inputs,
    zone_soil_inputs,
    status_mode,
):
  st.subheader("⚡ Central Retention Basin 3D Terrain & Telemetry")

  col_gauges, col_3d = st.columns([1, 1])

  with col_gauges:
    st.markdown("### 📊 Real-Time Hydro-Gauges")
    fig_g1 = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pond_level,
            title={"text": "Central Pond Capacity (%)"},
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
    fig_g1.update_layout(height=180, margin=dict(l=15, r=15, t=25, b=15))
    st.plotly_chart(fig_g1, width="stretch")

    fig_g2 = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=avg_soil_moisture,
            title={"text": "Avg Catchment Soil Moisture (% VWC)"},
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
    fig_g2.update_layout(height=180, margin=dict(l=15, r=15, t=25, b=15))
    st.plotly_chart(fig_g2, width="stretch")

  with col_3d:
    st.markdown("### 🏔️ 3D Simulated Retention Pond Geometry")

    grid_x = np.linspace(-10, 10, 40)
    grid_y = np.linspace(-10, 10, 40)
    X_grid, Y_grid = np.meshgrid(grid_x, grid_y)

    Z_basin = (X_grid**2 + Y_grid**2) * 0.25
    water_height = (pond_level / 100.0) * 25.0
    Z_water = np.full_like(X_grid, water_height)
    Z_water = np.minimum(Z_water, Z_basin)

    fig_3d = go.Figure()
    fig_3d.add_trace(
        go.Surface(
            z=Z_basin,
            x=X_grid,
            y=Y_grid,
            colorscale="YlOrBr",
            showscale=False,
            opacity=0.7,
            name="Pond Basin Terrain",
        )
    )
    fig_3d.add_trace(
        go.Surface(
            z=Z_water,
            x=X_grid,
            y=Y_grid,
            colorscale="Blues",
            showscale=False,
            opacity=0.85,
            name="Water Volume",
        )
    )

    fig_3d.update_layout(
        scene=dict(
            xaxis_title="Width (m)",
            yaxis_title="Length (m)",
            zaxis_title="Depth (m)",
            zaxis=dict(range=[0, 30]),
            aspectratio=dict(x=1, y=1, z=0.5),
        ),
        height=370,
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_3d, width="stretch")

  st.markdown("---")
  st.subheader("🎛️ Sub-Zone Actuator Telemetry Matrix")

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