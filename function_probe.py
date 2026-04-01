"""Quick probe script for validating ncr_lookup.get_location with live coordinates."""
from ncr_lookup import load_ncr, get_location


def run_probe():
    features = load_ncr("ncr_barangays_geojson.geojson")

    checks = [
        # README sample coordinate
        {
            "label": "README sample",
            "lat": 14.531659172292766,
            "lon": 121.0736745605332,
            "expected": {"barangay": "Tuktukan", "city": "Taguig"},
        },
        # In Manila Bay area (outside NCR barangay polygons)
        {
            "label": "Outside NCR",
            "lat": 14.2000,
            "lon": 121.2000,
            "expected": None,
        },
        # Midpoint sampled from a known Caloocan feature
        {
            "label": "Caloocan sample",
            "lat": 14.66749216,
            "lon": 120.99595985,
            "expected": {"barangay": "Barangay 149", "city": "Caloocan"},
        },
    ]

    for c in checks:
        actual = get_location(c["lat"], c["lon"], features)
        print(f"{c['label']}: input=({c['lat']}, {c['lon']})")
        print(f"  returned: {actual}")
        print(f"  expected: {c['expected']}")
        print(f"  correct : {actual == c['expected']}")


if __name__ == "__main__":
    run_probe()
