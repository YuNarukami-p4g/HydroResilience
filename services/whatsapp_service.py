# services/whatsapp_service.py
from datetime import datetime
import requests


def send_whatsapp_alert(wa_phone, wa_apikey, township, status_mode, pond_level, total_hourly_runoff_m3):
  msg_text = (
      f"⚠️ [SDP HYDRORESILIENCE ALERT]\nTownship: {township}\nStatus:"
      f" {status_mode}\nCentral Pond Level: {pond_level}%\nInflow Runoff:"
      f" {total_hourly_runoff_m3:,.0f} m³/h\nTimestamp:"
      f" {datetime.now().strftime('%Y-%m-%d %H:%M')}"
  )
  wa_url = f"https://api.callmebot.com/whatsapp.php?phone={wa_phone}&text={requests.utils.quote(msg_text)}&apikey={wa_apikey}"
  response = requests.get(wa_url, timeout=5)
  return response