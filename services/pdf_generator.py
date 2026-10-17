# services/pdf_generator.py
from datetime import datetime
from fpdf import FPDF


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

  pdf.cell(0, 6, f"Target Township: {township}", ln=1)
  pdf.cell(
      0,
      6,
      f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
      ln=1,
  )
  pdf.ln(4)

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