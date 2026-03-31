# NCR Barangay & City Lookup

## Overview
This Python script allows you to find the **barangay** and **city** in Metro Manila (NCR) given a latitude and longitude coordinate.  

It is **pure Python** with **no external dependencies** and is designed to be used as a **callable function** in scripts or applications.

---

## Usage
1. Ensure the GeoJSON file `ncr_barangays_geojson.geojson` is in the same directory as the script (or provide the path to `load_ncr()`).
2. Import the functions and load the data:

```python
from ncr_lookup import load_ncr, get_location

# Load NCR GeoJSON data
features = load_ncr("ncr_barangays_geojson.geojson")

# Lookup coordinates
lat, lon = 14.6091, 120.9890
result = get_location(lat, lon, features)

if result:
    print(f"Barangay: {result['barangay']}, City: {result['city']}")
else:
    print("Coordinates are outside NCR")