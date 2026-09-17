"""Package markers + shared constants."""
DIMENSIONS = ["soil", "climate", "biodiversity", "land_use", "human_impact"]

CRITICAL_VARS = [
    ("soil.organic_carbon_pct", "Soil Organic Carbon (%)"),
    ("climate.rainfall_mm", "Annual Rainfall (mm)"),
    ("land_use.dominant_type", "Land Use Type"),
    ("climate.temperature_c", "Mean Temperature (°C)"),
    ("biodiversity.pollinator_presence", "Pollinator Presence"),
    ("soil.ph", "Soil pH"),
]
