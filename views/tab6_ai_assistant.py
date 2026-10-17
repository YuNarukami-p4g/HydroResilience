# views/tab6_ai_assistant.py
import streamlit as st


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
):
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
            + ". Ask me about WhatsApp field alerts, 3D pond geometry, or PDF"
            " exports!"
        ),
    }]

  for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

  if prompt := st.chat_input("e.g., How are WhatsApp alerts dispatched?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    p_lower = prompt.lower()
    if "whatsapp" in p_lower or "alert" in p_lower or "notify" in p_lower:
      ans = (
          "Emergency field notifications are standardized on WhatsApp in Tab"
          " 5 ('Citizen Portal & WhatsApp Alerts'). Enter your phone number"
          " (+60...) and CallMeBot API key to receive automated flood alerts!"
      )
    elif "3d" in p_lower or "pond" in p_lower:
      ans = (
          "The 3D Retention Pond visualizer in Tab 2 dynamically adjusts water"
          " depth based on your central retention pond capacity slider."
      )
    elif "risk" in p_lower or "ml" in p_lower or "forecast" in p_lower:
      ans = (
          f"The XGBoost ML model predicts a peak pond level of **{ml_peak_level}%**"
          f" in the next 4 hours ({ml_risk_class}) with {ml_confidence}%"
          " confidence."
      )
    elif "save" in p_lower or "cost" in p_lower or "money" in p_lower:
      ans = (
          f"For a {park_size}-hectare landscape area, the system saves"
          f" **RM {annual_rm_saved:,.2f} annually** in utility water bills,"
          f" paying back the CapEx in **{payback_years:.1f} years**."
      )
    else:
      ans = (
          f"System normal across {selected_township}. Combined spatial inflow"
          f" runoff is {total_hourly_runoff_m3:,.1f} m³/h."
      )

    st.session_state.messages.append({"role": "assistant", "content": ans})
    st.chat_message("assistant").write(ans)