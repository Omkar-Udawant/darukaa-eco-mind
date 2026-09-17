"""Golden demo scenarios for docs / manual QA."""
SCENARIOS = [
    {"name": "degraded-cropland", "message": "Biodiversity is declining on my cropland near Nashik. SOC 0.6%, pH 6.8, rainfall 520mm, 34C, heavy pesticide, few bees."},
    {"name": "vague", "message": "Biodiversity is declining."},
    {"name": "forest-edge", "message": "Forest patch near Coorg, deforestation medium, fragmentation high, rainfall 1400mm, 26C, pollinators medium."},
    {"name": "urban-wetland", "message": "Urban wetland in Chennai, 42% urban, pollution high, rainfall 900mm, 33C, wetland birds declining."},
]

if __name__ == "__main__":
    for s in SCENARIOS:
        print(f"[{s['name']}] {s['message']}")
