from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))
import ncr_lookup

features = ncr_lookup.load_ncr(Path(__file__).parent / "ncr_barangays_geojson.geojson")
result = ncr_lookup.get_location(14.531659172292766,121.0736745605332, features)
print(result)