# config.py

TOWNSHIP_ZONES = {
    "City of Elmina": {
        "master_pond_capacity_m3": 250000,
        "zones": {
            "Elmina West (Residential Phase 1)": {
                "lat": 3.1706,
                "lon": 101.5230,
                "area_m2": 450000,
                "runoff_coeff": 0.65,
            },
            "Elmina Central Park (Green Basin)": {
                "lat": 3.1780,
                "lon": 101.5290,
                "area_m2": 600000,
                "runoff_coeff": 0.35,
            },
            "Elmina East (Commercial Hub)": {
                "lat": 3.1630,
                "lon": 101.5380,
                "area_m2": 350000,
                "runoff_coeff": 0.85,
            },
        },
    },
    "Bandar Bukit Raja": {
        "master_pond_capacity_m3": 180000,
        "zones": {
            "Bukit Raja Industrial Park": {
                "lat": 3.0738,
                "lon": 101.5183,
                "area_m2": 500000,
                "runoff_coeff": 0.90,
            },
            "Bukit Raja Wetlands (Zone A)": {
                "lat": 3.0810,
                "lon": 101.5250,
                "area_m2": 700000,
                "runoff_coeff": 0.30,
            },
            "Residential North Phase": {
                "lat": 3.0680,
                "lon": 101.5110,
                "area_m2": 400000,
                "runoff_coeff": 0.60,
            },
        },
    },
}

CUSTOM_CSS = """
    <style>
    .main-header {font-size:24px; font-weight:bold; color:#0e1117;}
    .status-banner {padding:12px; border-radius:8px; font-weight:bold; margin-bottom:15px;}
    .zone-card {background-color:#f8f9fa; padding:12px; border-radius:8px; border-left:4px solid #1E88E5; margin-bottom:10px;}
    .report-card {background-color:#eef6fc; padding:15px; border-radius:8px; border:1px solid #b6d4f1;}
    .citizen-card {background-color:#ffffff; padding:15px; border-radius:8px; border:1px solid #e0e0e0; margin-bottom:10px;}
    </style>
"""