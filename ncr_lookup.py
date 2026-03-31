"""
NCR Barangay & City Lookup
--------------------------
Given a lat/lon coordinate, returns the barangay and city in Metro Manila.

No external dependencies — pure Python standard library only.
"""

import json
import os

def _ray_cast(lon, lat, ring):
    """Return True if (lon, lat) is inside a polygon ring."""
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def _in_polygon(lon, lat, rings):
    """Polygon: inside outer ring and outside all hole rings."""
    if not _ray_cast(lon, lat, rings[0]):
        return False
    for hole in rings[1:]:
        if _ray_cast(lon, lat, hole):
            return False
    return True

def _in_geometry(lon, lat, geometry):
    """Check point against a GeoJSON Polygon or MultiPolygon."""
    if geometry["type"] == "Polygon":
        return _in_polygon(lon, lat, geometry["coordinates"])
    if geometry["type"] == "MultiPolygon":
        return any(_in_polygon(lon, lat, rings) for rings in geometry["coordinates"])
    return False

def load_ncr(path=None):
    """
    Load the NCR GeoJSON file and return a list of (geometry, barangay, city) tuples.
    If path is None, automatically looks for 'ncr_barangays_geojson.geojson' in the script folder.
    """
    if path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "ncr_barangays_geojson.geojson")

    with open(path, encoding="utf-8") as f:
        gj = json.load(f)

    return [
        (feat["geometry"], feat["properties"].get("adm4_en"), feat["properties"].get("city"))
        for feat in gj["features"]
    ]

def get_location(lat, lon, features):
    """
    Given lat/lon, return {'barangay': str, 'city': str} or None if outside NCR.
    """
    for geometry, barangay, city in features:
        if _in_geometry(lon, lat, geometry):
            return {"barangay": barangay, "city": city}
    return None

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)

    lat, lon = float(sys.argv[1]), float(sys.argv[2])
    features = load_ncr()
    result = get_location(lat, lon, features)

    if result:
        print(f"Barangay: {result['barangay']}")
        print(f"City    : {result['city']}")
    else:
        print("Not found (coordinates may be outside NCR)")