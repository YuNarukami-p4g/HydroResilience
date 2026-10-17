# views/tab7_duty_roster.py
import pandas as pd
import streamlit as st

ROSTER_DATA = {
    "City of Elmina": [
        {
            "Staff ID": "SDP-4012",
            "Name": "Ir. Ahmad Razali",
            "Role": "Lead Hydraulic Engineer",
            "Assigned Zone": "Elmina Central Park",
            "Shift": "07:00 - 15:00",
            "Status": "🟢 On Duty (In Field)",
            "Contact": "+60 12-345 6789",
        },
        {
            "Staff ID": "SDP-4088",
            "Name": "Suresh Kumar",
            "Role": "IoT Sensor Technician",
            "Assigned Zone": "Elmina West Phase 1",
            "Shift": "07:00 - 15:00",
            "Status": "🟢 On Duty (Control Room)",
            "Contact": "+60 13-987 6543",
        },
        {
            "Staff ID": "SDP-5102",
            "Name": "Nurul Huda",
            "Role": "Drainage Maintenance Supervisor",
            "Assigned Zone": "Elmina East Commercial",
            "Shift": "15:00 - 23:00",
            "Status": "🟡 On Call",
            "Contact": "+60 17-555 1234",
        },
    ],
    "Bandar Bukit Raja": [
        {
            "Staff ID": "SDP-3021",
            "Name": "Tan Wei Ming",
            "Role": "Township Asset Manager",
            "Assigned Zone": "Industrial Park Basin",
            "Shift": "08:00 - 17:00",
            "Status": "🟢 On Duty (On Site)",
            "Contact": "+60 16-222 3344",
        },
        {
            "Staff ID": "SDP-3090",
            "Name": "Mohd Hafiz",
            "Role": "Sluice Gate Operator",
            "Assigned Zone": "Wetlands Zone A",
            "Shift": "08:00 - 17:00",
            "Status": "🟢 On Duty (Control Room)",
            "Contact": "+60 19-444 8899",
        },
    ],
}


def render_tab7(selected_township):
  st.subheader(f"👷 {selected_township} On-Duty Field Personnel Roster")
  st.caption("Active shift assignments & hydraulic maintenance dispatch list")

  roster = ROSTER_DATA.get(selected_township, [])

  if roster:
    df_roster = pd.DataFrame(roster)

    # Summary Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total On-Duty Engineers", len(df_roster))
    m2.metric(
        "Active Field Personnel",
        sum(1 for r in roster if "In Field" in r["Status"] or "On Site" in r["Status"]),
    )
    m3.metric("Current Shift Window", "Morning Shift (07:00 - 15:00)")

    st.markdown("---")
    st.table(df_roster)

    st.markdown("### 📞 Quick Engineer Contact Cards")
    cols = st.columns(len(roster))
    for idx, staff in enumerate(roster):
      with cols[idx]:
        st.markdown(f"""
                <div style="background-color:#f8f9fa; padding:12px; border-radius:8px; border-top:4px solid #1E88E5;">
                    <b>{staff['Name']}</b><br>
                    <small>{staff['Role']}</small><br>
                    📍 <code>{staff['Assigned Zone']}</code><br>
                    📞 <b>{staff['Contact']}</b><br>
                    <span>{staff['Status']}</span>
                </div>
                """, unsafe_allow_html=True)
  else:
    st.info("No personnel currently assigned to this township sector.")