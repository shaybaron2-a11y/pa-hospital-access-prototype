"""Fetch official source data and build the static dashboard snapshot.

The dashboard is intentionally static, so this script materializes a dated
snapshot in data/. Run it again when the source releases are updated.
"""

import csv
import json
import math
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STATE = "42"
ACS_YEAR = "2024"
CMS_DATASET = "xubh-q36u"
CMS_LIMIT = 1500
CMS_URL = f"https://data.cms.gov/provider-data/api/1/datastore/query/{CMS_DATASET}/0"
TIGER_URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query"
GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/locations/address"
ACS_MIRROR_URL = "https://api.censusreporter.org/1.0/data/show/latest"

SOURCE_ACS = f"U.S. Census Bureau, American Community Survey {ACS_YEAR}"
SOURCE_ACS_CANONICAL_5YR = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5"
SOURCE_CMS = "U.S. Centers for Medicare & Medicaid Services, Hospital General Information"
SOURCE_CMS_CANONICAL = "https://data.cms.gov/provider-data/dataset/xubh-q36u"
SOURCE_TIGER = "U.S. Census Bureau, TIGERweb State/County boundaries"
SOURCE_GEOCODER = "U.S. Census Bureau, Census Geocoder"


def get_json(url, params=None):
    if params:
        url = f"{url}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "pa-hospital-access-prototype/1.0"})
    with urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def number(value):
    return float(value or 0)


def polygon_centroid(ring):
    """Return a planar centroid for one lon/lat ring."""
    area2 = 0.0
    cx = 0.0
    cy = 0.0
    for first, second in zip(ring, ring[1:] + ring[:1]):
        cross = first[0] * second[1] - second[0] * first[1]
        area2 += cross
        cx += (first[0] + second[0]) * cross
        cy += (first[1] + second[1]) * cross
    if not area2:
        return ring[0]
    return cx / (3 * area2), cy / (3 * area2)


def geometry_centroid(geometry):
    coordinates = geometry["coordinates"]
    if geometry["type"] == "Polygon":
        rings = coordinates
    else:
        rings = max((polygon for polygon in coordinates), key=lambda polygon: len(polygon[0]))
    return polygon_centroid(rings[0])


def fetch_counties():
    payload = get_json(TIGER_URL, {
        "where": f"STATE='{STATE}'",
        "outFields": "NAME,GEOID",
        "returnGeometry": "true",
        "f": "geojson",
    })
    counties = []
    for feature in payload["features"]:
        props = feature["properties"]
        lon, lat = geometry_centroid(feature["geometry"])
        counties.append({
            "geoid": props["GEOID"],
            "county": props["NAME"].replace(" County", ""),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "source_boundary": SOURCE_TIGER,
            "source_boundary_url": TIGER_URL,
        })
    return sorted(counties, key=lambda row: row["county"])


def fetch_acs(county):
    """Read ACS estimates through Census Reporter when the direct API key is unavailable.

    The release returned by the mirror is retained per county. Large counties
    may have a 1-year release while smaller counties use the 5-year release;
    the page exposes this provenance instead of hiding the difference.
    """
    geo_id = f"05000US{county['geoid']}"
    payload = get_json(ACS_MIRROR_URL, {
        "table_ids": "B01001,B17001,B27010",
        "geo_ids": geo_id,
    })
    data = payload["data"][geo_id]
    age = data["B01001"]["estimate"]
    poverty = data["B17001"]["estimate"]
    insurance = data["B27010"]["estimate"]
    total = number(age["B01001001"])
    age65_count = sum(number(age[f"B01001{i:03d}"]) for i in range(20, 26))
    age65_count += sum(number(age[f"B01001{i:03d}"]) for i in range(44, 50))
    poverty_total = number(poverty["B17001001"])
    uninsured_count = sum(number(insurance[f"B27010{i:03d}"]) for i in (17, 33, 50, 66))
    insurance_total = number(insurance["B27010001"])
    release = payload["release"]
    release_label = release["name"]
    release_dataset = "acs1" if "1-year" in release_label else "acs5"
    canonical_url = f"https://api.census.gov/data/{ACS_YEAR}/acs/{release_dataset}"
    mirror_url = f"{ACS_MIRROR_URL}?{urlencode({'table_ids': 'B01001,B17001,B27010', 'geo_ids': geo_id})}"
    return {
        **county,
        "population": int(total),
        "age65": round(age65_count / total * 100, 2),
        "poverty": round(number(poverty["B17001002"]) / poverty_total * 100, 2),
        "uninsured": round(uninsured_count / insurance_total * 100, 2),
        "acs_release": release_label,
        "source_acs": f"{SOURCE_ACS} {release_label} (via Census Reporter mirror)",
        "source_acs_url": canonical_url,
        "source_acs_retrieval_url": mirror_url,
    }


def fetch_hospitals():
    payload = get_json(CMS_URL, {"offset": 0, "count": "false", "limit": CMS_LIMIT, "conditions[0][property]": "state", "conditions[0][value]": "PA"})
    rows = []
    for row in payload["results"]:
        if row.get("hospital_type") != "Acute Care Hospitals":
            continue
        address = {
            "street": row.get("address", ""),
            "city": row.get("citytown", ""),
            "state": row.get("state", "PA"),
            "zip": row.get("zip_code", ""),
        }
        try:
            geo = get_json(GEOCODER_URL, {**address, "benchmark": "Public_AR_Current", "format": "json"})
            matches = geo["result"]["addressMatches"]
            if not matches:
                continue
            coordinates = matches[0]["coordinates"]
            lon, lat = float(coordinates["x"]), float(coordinates["y"])
        except (KeyError, ValueError, IndexError):
            continue
        rows.append({
            "facility_id": row.get("facility_id", ""),
            "facility_name": row.get("facility_name", ""),
            "county": row.get("countyparish", "").title(),
            "hospital_type": row.get("hospital_type", ""),
            "emergency_services": row.get("emergency_services", ""),
            "hospital_ownership": row.get("hospital_ownership", ""),
            "address": address["street"],
            "city": address["city"],
            "zip": address["zip"],
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "source_cms": SOURCE_CMS,
            "source_cms_url": SOURCE_CMS_CANONICAL,
            "source_geocoder": SOURCE_GEOCODER,
            "source_geocoder_url": GEOCODER_URL,
        })
        time.sleep(0.05)
    return rows


def haversine_miles(lat1, lon1, lat2, lon2):
    radius = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def build_rows(counties, hospitals):
    by_county = {}
    for hospital in hospitals:
        by_county.setdefault(hospital["county"], []).append(hospital)
    for county in counties:
        county_hospitals = hospitals
        distances = [haversine_miles(county["lat"], county["lon"], h["lat"], h["lon"]) for h in county_hospitals]
        county["hospitals"] = len(by_county.get(county["county"], []))
        county["nearest"] = round(min(distances), 1) if distances else None
        county["rate"] = round(county["hospitals"] / county["population"] * 100000, 2)
        county["density_class"] = "Rural" if county["population"] < 100000 else "County market"
        county["source_density_class"] = "Derived from ACS population threshold; not an official rurality designation"
        county["source_hospital_count"] = SOURCE_CMS
        county["source_hospital_count_url"] = SOURCE_CMS_CANONICAL
        county["source_nearest"] = "Derived: county boundary centroid + geocoded CMS hospital addresses"
        county["source_nearest_url"] = f"{TIGER_URL} | {GEOCODER_URL}"
        county["source_rate"] = "Derived: CMS hospital count / ACS population * 100,000"
        county["source_rate_url"] = f"{SOURCE_CMS_CANONICAL} | {SOURCE_ACS_CANONICAL_5YR}"
    return counties


def write_csv(path, rows):
    path.parent.mkdir(exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    retrieved_at = date.today().isoformat()
    counties = fetch_counties()
    enriched = []
    for index, county in enumerate(counties, start=1):
        print(f"ACS {index}/{len(counties)} {county['county']}")
        enriched.append(fetch_acs(county))
    hospitals = fetch_hospitals()
    rows = build_rows(enriched, hospitals)
    for row in rows:
        row["retrieved_at"] = retrieved_at
    for row in hospitals:
        row["retrieved_at"] = retrieved_at
    write_csv(DATA / "pa_county_access_official.csv", rows)
    write_csv(DATA / "pa_hospitals_official.csv", hospitals)
    snapshot = {"retrieved_at": retrieved_at, "counties": rows, "hospitals": hospitals}
    (DATA / "pa_access_official.js").write_text("window.PA_ACCESS_DATA = " + json.dumps(snapshot, ensure_ascii=False) + ";\n", encoding="utf-8")
    (DATA / "pa_access_metadata.json").write_text(json.dumps({
        "retrieved_at": retrieved_at,
        "county_source": SOURCE_ACS,
        "county_source_url": "https://api.census.gov/data/2024/acs/acs5 and https://api.census.gov/data/2024/acs/acs1",
        "hospital_source": SOURCE_CMS,
        "hospital_source_url": SOURCE_CMS_CANONICAL,
        "geometry_source": SOURCE_TIGER,
        "geometry_source_url": TIGER_URL,
        "geocoder_source": SOURCE_GEOCODER,
        "geocoder_source_url": GEOCODER_URL,
        "notes": "ACS values are retrieved through Census Reporter when the Census API key is unavailable; release is retained per county.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} counties and {len(hospitals)} hospitals")


if __name__ == "__main__":
    main()
