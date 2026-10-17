# views/tab3_weather_ml.py
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_tab3(
    ml_peak_level,
    ml_risk_class,
    ml_confidence,
    ml_risk_color,
    forecast_times,
    forecast_precip,
    pond_level,
):
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
    st.plotly_chart(fig_forecast, width='stretch')