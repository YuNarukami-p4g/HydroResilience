# views/tab5_citizen_alerts.py
from datetime import datetime
import pandas as pd
from PIL import Image
import streamlit as st


def render_tab5(
    selected_township,
    status_mode,
    pond_level,
    total_hourly_runoff_m3,
    township_data,
):
  st.subheader("📋 Emergency Alert Payload & Resident Incident Portal")
  col_push, col_portal = st.columns(2)

  with col_push:
    st.markdown("### 📤 Automated Emergency Alert Payload")
    st.caption("1-click copyable notification payload for field teams:")

    # Generate standardized alert text
    alert_payload = (
        f"⚠️ [SDP HYDRORESILIENCE ALERT]\n"
        f"Township: {selected_township}\n"
        f"Operational Mode: {status_mode}\n"
        f"Retention Basin Capacity: {pond_level}%\n"
        f"Spatial Runoff Rate: {total_hourly_runoff_m3:,.0f} m³/h\n"
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Action: Pre-discharge sluice gates actuated. Inspect sub-zone"
        " swales."
    )

    if status_mode == "CRITICAL_DISCHARGE":
      st.error(
          "⚠️ CRITICAL DISCHARGE ACTIVE: Copy payload below for field team"
          " dispatch."
      )
    else:
      st.info("System Normal: Pre-formatted dispatch payload ready below.")

    # Streamlit code box natively provides a 1-click 'Copy to Clipboard' button
    st.code(alert_payload, language="text")

    st.toast("💡 Hover over the top-right of the box above to copy message!")

  with col_portal:
    st.markdown("### 📸 Submit Resident Flood / Drain Incident")
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
        img_obj = Image.open(rep_photo) if rep_photo is not None else None

        new_rep = {
            "id": f"REP-{len(st.session_state.citizen_reports)+101}",
            "zone": rep_zone.split(" (")[0],
            "category": rep_cat,
            "desc": rep_desc,
            "status": "In Progress",
            "time": "Just now",
            "image": img_obj,
        }
        st.session_state.citizen_reports.insert(0, new_rep)
        st.success("Incident logged! SDP Operations team notified.")

  st.markdown("---")
  st.subheader("📋 Resident Incident Management Log")

  for idx, rep in enumerate(st.session_state.citizen_reports):
    badge_color = "#E53935" if rep["status"] == "In Progress" else "#43A047"

    with st.expander(
        f"📌 [{rep['id']}] {rep['category']} — {rep['zone']} ({rep['status']})",
        expanded=(idx == 0),
    ):
      c_info, c_action = st.columns([2, 1])

      with c_info:
        st.write(f"**Description**: {rep['desc']}")
        st.caption(f"🕒 Reported: {rep['time']}")

        if rep["image"] is not None:
          st.image(
              rep["image"],
              caption=f"Photo Upload ({rep['id']})",
              width=280,
          )
        else:
          st.info("📷 No photo attached for this report.")

      with c_action:
        st.markdown(
            f"**Current Status**: <span"
            f" style='color:{badge_color}; font-weight:bold;'>{rep['status']}</span>",
            unsafe_allow_html=True,
        )

        if rep["status"] != "Completed / Resolved":
          if st.button(
              "✅ Mark as Resolved / Completed", key=f"btn_resolve_{rep['id']}"
          ):
            rep["status"] = "Completed / Resolved"
            st.success(f"Report {rep['id']} marked as Resolved!")
            st.rerun()