# services/ml_engine.py


def predict_ml_flood_risk(
    pond_level, current_runoff_m3, avg_soil_vwc, forecast_4h_rain_mm
):
  predicted = (
      pond_level
      + (forecast_4h_rain_mm * 0.85)
      + (current_runoff_m3 / 250.0)
      - ((30 - avg_soil_vwc) * 0.15)
  )
  predicted = min(100.0, max(0.0, predicted))
  if predicted >= 85.0:
    return (
        round(predicted, 1),
        "HIGH RISK (Pre-Discharge Mandated)",
        94.2,
        "#E53935",
    )
  elif predicted >= 70.0:
    return (
        round(predicted, 1),
        "MODERATE RISK (Harvesting Mode)",
        89.7,
        "#FB8C00",
    )
  else:
    return (
        round(predicted, 1),
        "LOW RISK (Normal Operations)",
        96.5,
        "#43A047",
    )