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

  # -------------------------------------------------------------------
  # FAULT DETECTION & MANUAL OVERRIDE CONTROLS
  # -------------------------------------------------------------------
  with st.expander("🛠️ Operational Control, Hysteresis & Maintenance Overrides", expanded=False):
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
      sensor_fault_sim = st.checkbox("⚠️ Simulate Level Sensor Fault", value=False)
    with col_ctrl2:
      manual_override_gate = st.checkbox("🔓 Manual Override: Force Open Sluice Gate", value=False)
    with col_ctrl3:
      manual_override_pump = st.checkbox("🔌 Manual Override: Force Run Irrigation Pumps", value=False)

  # Evaluate Explicit Control Reasons & Decision Banners
  decision_reasons = []
  if sensor_fault_sim:
    decision_reasons.append("⚠️ FAULT DETECTED: Level sensor reading out-of-bounds / disconnected. Fail-safe standby engaged.")
  elif pond_level <= 15:
    decision_reasons.append("🛑 LOW TANK LOCKOUT: Stored water level ≤ 15%. Irrigation pumps locked out to prevent dry run damage.")
  elif pond_level > 80:
    decision_reasons.append("🚨 HIGH WATER LEVEL: Retention capacity > 80%. Pre-discharge sluice gates activated.")

  if manual_override_gate:
    decision_reasons.append("🔧 MANUAL OVERRIDE ACTIVE: Main sluice gate forced 100% OPEN by maintenance operator.")
  if manual_override_pump:
    decision_reasons.append("🔧 MANUAL OVERRIDE ACTIVE: Sub-surface irrigation pumps forced ON by maintenance operator.")

  if avg_soil_moisture < 25 and pond_level > 15 and not sensor_fault_sim:
    decision_reasons.append("🌱 IRRIGATION DEMAND: Soil VWC < 25% lower threshold + Stored water available → Irrigation started.")
  elif avg_soil_moisture >= 40:
    decision_reasons.append("⏸️ SOIL SATISFIED: Soil VWC ≥ 40% upper hysteresis threshold → Irrigation paused.")

  if decision_reasons:
    for reason in decision_reasons:
      if "FAULT" in reason or "CRITICAL" in reason or "🚨" in reason or "🛑" in reason:
        st.error(reason)
      elif "MANUAL" in reason or "🔧" in reason:
        st.warning(reason)
      else:
        st.info(reason)

  # -------------------------------------------------------------------
  # GAUGES & REALISTIC 3D RETENTION BASIN
  # -------------------------------------------------------------------
  col_gauges, col_3d = st.columns([1, 1])

  with col_gauges:
    st.markdown("### 📊 Real-Time Hydro-Gauges")
    
    display_pond_level = 0.0 if sensor_fault_sim else pond_level
    fig_g1 = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=display_pond_level,
            title={"text": "Central Pond Capacity (%)" + (" [SENSOR FAULT]" if sensor_fault_sim else "")},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#C62828" if sensor_fault_sim else "#1E88E5"},
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
    st.markdown("### 🏔️ Civil-Engineered Retention Pond 3D Geometry")

    # 1. High-Resolution Rectangular Mesh Grid
    x = np.linspace(-24, 24, 70)
    y = np.linspace(-16, 16, 70)
    X_grid, Y_grid = np.meshgrid(x, y)

    # Trapezoidal Basin Dimensions (Flat bed: 20m x 12m, Depth: 5.0m max)
    w_bed, l_bed = 10.0, 6.0
    depth_max = 5.0
    
    # Distance calculation to inner flat bed rectangle (with smooth rounded corners)
    dx = np.maximum(0, np.abs(X_grid) - w_bed)
    dy = np.maximum(0, np.abs(Y_grid) - l_bed)
    dist = np.sqrt(dx**2 + dy**2)
    
    # Terrain height: flat at center (0m), 1:2.2 sloped walls up to top crest (5.0m)
    Z_basin = np.minimum(depth_max, dist * 0.75)

    # Cut Swale Inlet Channel into Left Bank (X: -24 to -10, Y: -2 to +2)
    inlet_mask = (X_grid < -10) & (np.abs(Y_grid) < 2.5)
    Z_basin[inlet_mask] = np.minimum(Z_basin[inlet_mask], 1.5)

    # Cut Outflow Spillway Channel into Right Bank (X: 10 to 24, Y: -2 to +2)
    spillway_mask = (X_grid > 10) & (np.abs(Y_grid) < 2.5)
    Z_basin[spillway_mask] = np.minimum(Z_basin[spillway_mask], 3.8)

    # 2. Water Elevation & Clipping
    water_height = (display_pond_level / 100.0) * depth_max
    
    # Mask out water surface points where ground elevation is higher than water level
    Z_water_surface = np.where(Z_basin <= water_height + 0.02, water_height, np.nan)

    # 3. Build Plotly 3D Figure
    fig_3d = go.Figure()

    # Custom Earth-to-Grass Palette for Civil Pond Topography
    terrain_colorscale = [
        [0.0, '#3e2723'],   # Dark silt/mud basin bed
        [0.18, '#5d4037'],  # Wet sediment transition
        [0.38, '#8d6e63'],  # Clay/gravel sloped embankments
        [0.62, '#689f38'],  # Turf slope
        [1.0, '#2e7d32']    # Lush green crest/berm
    ]

    # Render Basin Topography Surface
    fig_3d.add_trace(
        go.Surface(
            z=Z_basin,
            x=X_grid,
            y=Y_grid,
            colorscale=terrain_colorscale,
            showscale=False,
            name="Pond Structure",
            hovertemplate="X: %{x:.1f}m<br>Y: %{y:.1f}m<br>Elevation: %{z:.2f}m<extra>Basin Slope</extra>"
        )
    )

    # Render Clipped Stormwater Body Surface
    if display_pond_level > 0:
      fig_3d.add_trace(
          go.Surface(
              z=Z_water_surface,
              x=X_grid,
              y=Y_grid,
              colorscale=[[0, '#00b0ff'], [1, '#01579b']],
              showscale=False,
              opacity=0.82,
              name="Stored Stormwater Volume",
              hovertemplate=f"Water Elevation: {water_height:.2f}m ({display_pond_level:.0f}%)<extra>Water Volume</extra>"
          )
      )

    # 4. Add Concrete Sluice Gate Control Tower (Right Outflow)
    tower_x = [12, 12, 14, 14, 12, 12, 14, 14]
    tower_y = [-2.5, 2.5, 2.5, -2.5, -2.5, 2.5, 2.5, -2.5]
    tower_z = [0, 0, 0, 0, 6, 6, 6, 6]
    fig_3d.add_trace(
        go.Mesh3d(
            x=tower_x, y=tower_y, z=tower_z,
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 5, 3, 6, 7, 1, 1, 5, 5, 7, 7],
            color='#78909c',
            opacity=0.9,
            name="Concrete Sluice Tower"
        )
    )

    # Vertical Water Depth Staff Gauge Pole (Center Side Bank)
    gauge_z = np.linspace(0, 5.5, 20)
    gauge_x = np.full_like(gauge_z, 0)
    gauge_y = np.full_like(gauge_z, -7)
    fig_3d.add_trace(
        go.Scatter3d(
            x=gauge_x, y=gauge_y, z=gauge_z,
            mode="lines+markers",
            line=dict(color="#ffd600", width=6),
            marker=dict(size=3, color="black"),
            name="Depth Staff Gauge",
            hovertext=[f"Depth Mark: {z:.1f}m" for z in gauge_z]
        )
    )

    # Critical 80% Pre-Discharge Level Line
    crit_z = 4.0  # 80% of 5.0m depth
    ring_x = np.array([-12, 12, 12, -12, -12])
    ring_y = np.array([-8, -8, 8, 8, -8])
    ring_z = np.full_like(ring_x, crit_z)
    fig_3d.add_trace(
        go.Scatter3d(
            x=ring_x, y=ring_y, z=ring_z,
            mode="lines",
            line=dict(color="red", width=4, dash="dash"),
            name="80% Pre-Discharge Threshold"
        )
    )

    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(title="Width (m)", range=[-25, 25], backgroundcolor="#f1f8e9"),
            yaxis=dict(title="Length (m)", range=[-18, 18], backgroundcolor="#f1f8e9"),
            zaxis=dict(title="Depth (m)", range=[0, 7], backgroundcolor="#e8f5e9"),
            aspectratio=dict(x=1.3, y=1.0, z=0.45),
            camera=dict(
                eye=dict(x=1.45, y=-1.45, z=1.1)
            )
        ),
        height=390,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01)
    )
    st.plotly_chart(fig_3d, width="stretch")

  st.markdown("---")
  st.subheader("🎛️ Sub-Zone Actuator Telemetry Matrix & Manual Override")

  actuator_data = []
  for z_name, z_props in township_data["zones"].items():
    z_rain = zone_rain_inputs[z_name]
    z_soil = zone_soil_inputs[z_name]

    if sensor_fault_sim:
      inflow_valve = "0% CLOSED (FAIL-SAFE)"
      outflow_gate = "0% CLOSED (FAIL-SAFE)"
      sub_pump = "OFF (FAIL-SAFE)"
    else:
      inflow_valve = (
          "100% OPEN" if (z_rain >= 5.0 and pond_level < 90) else "0% CLOSED"
      )
      
      if manual_override_gate:
        outflow_gate = "100% OPEN (MANUAL OVERRIDE)"
      else:
        outflow_gate = (
            "100% OPEN" if status_mode == "CRITICAL_DISCHARGE" else "0% CLOSED"
        )
      
      if manual_override_pump:
        sub_pump = "ON (120 L/min) [MANUAL]"
      elif pond_level <= 15:
        sub_pump = "OFF (LOW TANK LOCKOUT)"
      elif z_soil < 25 and z_rain < 5.0:
        sub_pump = "ON (120 L/min)"
      else:
        sub_pump = "OFF"

    actuator_data.append({
        "Sub-Zone": z_name,
        "Local Rain (mm/h)": z_rain,
        "Soil Moisture (% VWC)": z_soil,
        "Inflow Swale Valve": inflow_valve,
        "Main Sluice Gate": outflow_gate,
        "Sub-Surface Pump": sub_pump,
    })

  st.dataframe(pd.DataFrame(actuator_data), width='stretch')