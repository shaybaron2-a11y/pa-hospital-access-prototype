import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"


COUNTIES = [
    {"county": "Philadelphia", "lat": 39.9526, "lon": -75.1652, "population": 1550542, "type": "Urban core", "hospitals": 20},
    {"county": "Allegheny", "lat": 40.4406, "lon": -79.9959, "population": 1230000, "type": "Urban core", "hospitals": 18},
    {"county": "Montgomery", "lat": 40.2290, "lon": -75.3879, "population": 860000, "type": "Suburban", "hospitals": 8},
    {"county": "Bucks", "lat": 40.3369, "lon": -75.1071, "population": 646000, "type": "Suburban", "hospitals": 5},
    {"county": "Delaware", "lat": 39.9168, "lon": -75.3879, "population": 576000, "type": "Suburban", "hospitals": 5},
    {"county": "Lancaster", "lat": 40.0379, "lon": -76.3055, "population": 553000, "type": "Small metro", "hospitals": 4},
    {"county": "Centre", "lat": 40.7934, "lon": -77.8600, "population": 158000, "type": "College/rural", "hospitals": 1},
    {"county": "Erie", "lat": 42.1292, "lon": -80.0851, "population": 270000, "type": "Small metro", "hospitals": 3},
    {"county": "Luzerne", "lat": 41.2459, "lon": -75.8813, "population": 326000, "type": "Small metro", "hospitals": 3},
    {"county": "Lycoming", "lat": 41.2412, "lon": -77.0011, "population": 114000, "type": "Rural", "hospitals": 1},
    {"county": "Tioga", "lat": 41.7487, "lon": -77.3005, "population": 41000, "type": "Rural", "hospitals": 0},
    {"county": "Cameron", "lat": 41.4388, "lon": -78.1986, "population": 4500, "type": "Rural", "hospitals": 0},
]

HOSPITALS = [
    {"name": "Hospital cluster: Philadelphia", "county": "Philadelphia", "lat": 39.9526, "lon": -75.1652, "category": "Major academic/urban cluster"},
    {"name": "Hospital cluster: Pittsburgh", "county": "Allegheny", "lat": 40.4406, "lon": -79.9959, "category": "Major academic/urban cluster"},
    {"name": "Hospital cluster: Montgomery County", "county": "Montgomery", "lat": 40.2290, "lon": -75.3879, "category": "Suburban hospital cluster"},
    {"name": "Hospital cluster: Bucks County", "county": "Bucks", "lat": 40.3369, "lon": -75.1071, "category": "Suburban hospital cluster"},
    {"name": "Hospital cluster: Delaware County", "county": "Delaware", "lat": 39.9168, "lon": -75.3879, "category": "Suburban hospital cluster"},
    {"name": "Lancaster General area", "county": "Lancaster", "lat": 40.0379, "lon": -76.3055, "category": "Small metro hospital"},
    {"name": "Mount Nittany Medical Center area", "county": "Centre", "lat": 40.7934, "lon": -77.8600, "category": "Regional hospital"},
    {"name": "Erie hospital area", "county": "Erie", "lat": 42.1292, "lon": -80.0851, "category": "Small metro hospital"},
    {"name": "Wilkes-Barre/Scranton area", "county": "Luzerne", "lat": 41.2459, "lon": -75.8813, "category": "Small metro hospital"},
    {"name": "Williamsport regional area", "county": "Lycoming", "lat": 41.2412, "lon": -77.0011, "category": "Regional hospital"},
]


def haversine_miles(lat1, lon1, lat2, lon2):
    radius = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def build_metrics():
    rows = []
    for county in COUNTIES:
        distances = [
            haversine_miles(county["lat"], county["lon"], h["lat"], h["lon"])
            for h in HOSPITALS
        ]
        nearest = min(distances)
        per_100k = county["hospitals"] / county["population"] * 100000
        risk = "High access burden" if nearest > 25 or county["hospitals"] == 0 else (
            "Moderate access burden" if nearest > 15 or per_100k < 1.0 else "Lower access burden"
        )
        rows.append({**county, "nearest_hospital_miles": round(nearest, 1), "hospitals_per_100k": round(per_100k, 2), "access_group": risk})
    return rows


def write_csv(rows):
    DATA.mkdir(exist_ok=True)
    with (DATA / "pa_county_access_prototype.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with (DATA / "pa_hospital_reference_points.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(HOSPITALS[0].keys()))
        writer.writeheader()
        writer.writerows(HOSPITALS)


def write_readme(rows):
    severity = {
        "High access burden": 3,
        "Moderate access burden": 2,
        "Lower access burden": 1,
    }
    top_risk = sorted(
        rows,
        key=lambda r: (severity[r["access_group"]], r["nearest_hospital_miles"], -r["hospitals_per_100k"]),
        reverse=True,
    )[:5]
    readme = f"""# Pennsylvania Hospital Access Prototype

## Research question

Do Pennsylvania counties show unequal spatial access to hospital care, and how could a student combine geography, public health, and hospital-system thinking to identify areas that may need better referral networks, telehealth support, or transportation planning?

## Why this project fits my academic direction

This project is designed as a small research sample for faculty outreach. It connects:

- health geography and GIS;
- hospital access and regional inequality;
- public health policy;
- hospital administration and planning.

My long-term interest is to work with physicians and public hospital systems on resource allocation, patient access, and health-system management.

## Prototype findings

- Rural counties in the sample show the highest access burden because they have either no local hospital point in the prototype or a longer distance to the nearest regional hospital.
- Large urban counties have far more hospitals, but population pressure means hospitals per 100,000 residents can still be an important second metric.
- The strongest next research step is to replace county centroids with census tract/block-group population centers and use drive-time networks rather than straight-line distance.

Highest-burden counties in this prototype:

| County | Type | Nearest hospital miles | Hospitals per 100k | Access group |
|---|---:|---:|---:|---|
"""
    for row in top_risk:
        readme += f"| {row['county']} | {row['type']} | {row['nearest_hospital_miles']} | {row['hospitals_per_100k']} | {row['access_group']} |\n"
    readme += """
## Files

- `figures/interactive_hospital_access_map.html`: interactive map-style dashboard for professor outreach.
- `data/pa_county_access_prototype.csv`: county-level access metrics used by the dashboard.
- `data/pa_hospital_reference_points.csv`: hospital reference points used for nearest-distance calculations.
- `scripts/build_project.py`: reproducible script that generates the data, dashboard, and outreach materials.
- `professor_email_template.md`: email template for contacting faculty.
- `one_page_project_pitch.md`: one-page project summary suitable for attaching to an email.

## Important note on data

This is a polished prototype, not a final peer-reviewed dataset. County populations and hospital locations are simplified reference values used to demonstrate a research workflow. A stronger version should use:

- HIFLD or CMS provider-level hospital data;
- Census ACS population by tract or block group;
- road-network travel time using ArcGIS Network Analyst, OpenRouteService, or OSRM;
- hospital service type, bed capacity, and emergency department availability.

## Methods

1. Define county reference points and hospital reference points.
2. Calculate great-circle distance from each county to the nearest hospital point.
3. Compute hospitals per 100,000 residents.
4. Classify counties into lower, moderate, or high access burden.
5. Visualize the relationship between geography, population, and hospital access.

## How I would expand this with a professor

- Move from counties to census tracts.
- Compare straight-line distance with true drive-time access.
- Add age structure, income, insurance status, and rurality.
- Build a model predicting high access burden.
- Connect findings to hospital referral networks and public health planning.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


def write_pitch():
    pitch = """# One-page project pitch

**Working title:** Spatial inequality in hospital access across Pennsylvania

**Core idea:** I want to understand how healthcare resources are distributed across space and whether rural or lower-resource communities face a higher access burden when seeking hospital care.

**Research question:** Which Pennsylvania counties appear to have weaker geographic access to hospitals, and how could hospital systems or public agencies use spatial analysis to plan referral networks, transportation support, telehealth, or regional partnerships?

**Why it matters:** Hospital care is not only a clinical issue. It is also a geography, management, and public policy issue. Patients may live far from hospitals, hospitals may be concentrated in urban academic centers, and public systems need better ways to identify access gaps.

**Current prototype:** I built a small reproducible prototype using county-level population, hospital reference points, nearest-distance calculations, hospitals per 100,000 residents, and an interactive dashboard.

**What I want to learn next:** I hope to work with a faculty mentor to improve this project using official provider data, Census tract data, real drive-time analysis, and stronger public health methods.

**Skills I can contribute now:** literature review, data cleaning, Excel/CSV work, basic statistics, GIS mapping, healthcare system background research, and China healthcare context from my Sinopharm internship.
"""
    (ROOT / "one_page_project_pitch.md").write_text(pitch, encoding="utf-8")


def write_email():
    email = """Subject: Undergraduate interested in health geography and hospital access research

Dear Professor [Last Name],

My name is [Your Name], and I am a sophomore at Penn State interested in the intersection of healthcare, geography, and public health. I am especially interested in hospital access, medical resource distribution, and how public health systems can use spatial analysis to support better planning.

I recently built a small prototype project on Pennsylvania hospital access. It compares county-level population, hospital reference points, nearest-hospital distance, and hospitals per 100,000 residents. The project is still preliminary, but I used it to practice turning a healthcare question into a reproducible spatial analysis workflow.

I read your work on [specific paper/project], especially your discussion of [specific detail]. I would be grateful for the opportunity to assist with your research, even through literature review, data cleaning, mapping, or basic analysis.

Would you be open to a 15-minute meeting sometime in the next few weeks? I would appreciate any advice on whether my interests could fit your current projects.

Best regards,
[Your Name]
"""
    (ROOT / "professor_email_template.md").write_text(email, encoding="utf-8")


def write_html(rows):
    payload = json.dumps({"counties": rows, "hospitals": HOSPITALS}, ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pennsylvania Hospital Access Prototype</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8f5;
      --ink: #17201b;
      --muted: #5f6c64;
      --line: #ccd5ce;
      --green: #2e7d64;
      --gold: #c98b27;
      --red: #b14a42;
      --blue: #2f6690;
      --panel: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px; }}
    header {{ display: grid; grid-template-columns: 1.4fr .8fr; gap: 20px; align-items: end; margin-bottom: 22px; }}
    h1 {{ font-size: clamp(26px, 4vw, 48px); line-height: 1.02; margin: 0 0 12px; letter-spacing: 0; }}
    p {{ margin: 0; color: var(--muted); line-height: 1.55; }}
    .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }}
    .stat, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .stat b {{ display: block; font-size: 28px; margin-bottom: 4px; }}
    .stat span {{ color: var(--muted); font-size: 13px; }}
    .grid {{ display: grid; grid-template-columns: 1.15fr .85fr; gap: 16px; align-items: start; }}
    .map-wrap {{ position: relative; min-height: 560px; }}
    svg {{ width: 100%; height: auto; display: block; }}
    .county {{ cursor: pointer; transition: opacity .15s ease, stroke-width .15s ease; }}
    .county:hover, .county.active {{ stroke-width: 3; opacity: .9; }}
    .hospital {{ fill: var(--blue); stroke: var(--panel); stroke-width: 1.5; }}
    .label {{ font-size: 12px; fill: var(--muted); pointer-events: none; }}
    .legend {{ display: flex; gap: 14px; flex-wrap: wrap; margin-top: 12px; color: var(--muted); font-size: 13px; }}
    .key {{ display: inline-flex; align-items: center; gap: 6px; }}
    .swatch {{ width: 12px; height: 12px; border-radius: 2px; display: inline-block; }}
    .detail h2 {{ margin: 0 0 10px; font-size: 22px; }}
    .detail dl {{ display: grid; grid-template-columns: 1fr auto; gap: 10px 14px; margin: 16px 0; }}
    dt {{ color: var(--muted); }}
    dd {{ margin: 0; font-weight: 600; }}
    .bar-row {{ display: grid; grid-template-columns: 92px 1fr 64px; gap: 10px; align-items: center; margin: 9px 0; font-size: 13px; }}
    .track {{ height: 9px; background: #e8ede9; border-radius: 999px; overflow: hidden; }}
    .fill {{ height: 100%; background: var(--green); border-radius: 999px; }}
    .note {{ margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--line); font-size: 14px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }}
    th, td {{ padding: 9px 8px; border-bottom: 1px solid var(--line); text-align: left; }}
    th {{ color: var(--muted); font-weight: 600; }}
    @media (max-width: 860px) {{
      main {{ padding: 18px; }}
      header, .grid {{ grid-template-columns: 1fr; }}
      .stats {{ grid-template-columns: 1fr; }}
      .map-wrap {{ min-height: auto; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <section>
      <h1>Spatial inequality in hospital access across Pennsylvania</h1>
      <p>A prototype research dashboard connecting geography, public health, and hospital-system planning. Click a county marker to inspect distance to the nearest hospital reference point and hospital supply per 100,000 residents.</p>
    </section>
    <section class="stats" aria-label="Project summary">
      <div class="stat"><b id="countyCount">12</b><span>counties sampled</span></div>
      <div class="stat"><b id="highCount">0</b><span>high-burden counties</span></div>
      <div class="stat"><b id="avgDistance">0</b><span>avg. nearest miles</span></div>
    </section>
  </header>
  <section class="grid">
    <section class="panel map-wrap">
      <svg id="map" viewBox="0 0 760 570" role="img" aria-label="Schematic map of sampled Pennsylvania county access metrics">
        <rect x="30" y="30" width="700" height="480" rx="24" fill="#eef3ef" stroke="#ccd5ce"></rect>
        <path d="M85 200 L185 105 L370 80 L575 120 L690 245 L650 405 L445 465 L245 440 L95 335 Z" fill="#dde8df" stroke="#9ca9a0" stroke-width="2"></path>
        <g id="counties"></g>
        <g id="hospitals"></g>
      </svg>
      <div class="legend">
        <span class="key"><span class="swatch" style="background: var(--green)"></span>Lower burden</span>
        <span class="key"><span class="swatch" style="background: var(--gold)"></span>Moderate burden</span>
        <span class="key"><span class="swatch" style="background: var(--red)"></span>High burden</span>
        <span class="key"><span class="swatch" style="background: var(--blue); border-radius: 50%"></span>Hospital reference point</span>
      </div>
    </section>
    <aside class="panel detail" aria-live="polite">
      <h2 id="detailCounty">Select a county</h2>
      <p id="detailIntro">This panel updates with access metrics and a professor-facing interpretation.</p>
      <dl>
        <dt>County type</dt><dd id="detailType">-</dd>
        <dt>Population</dt><dd id="detailPop">-</dd>
        <dt>Nearest hospital</dt><dd id="detailMiles">-</dd>
        <dt>Hospitals per 100k</dt><dd id="detailRate">-</dd>
        <dt>Access group</dt><dd id="detailGroup">-</dd>
      </dl>
      <div id="bars"></div>
      <p class="note" id="detailNote">Use this prototype to ask a professor about replacing county centroids with census-tract population centers and drive-time networks.</p>
    </aside>
  </section>
  <section class="panel" style="margin-top:16px">
    <strong>Ranked access burden table</strong>
    <table>
      <thead><tr><th>County</th><th>Type</th><th>Nearest miles</th><th>Hospitals / 100k</th><th>Group</th></tr></thead>
      <tbody id="tableBody"></tbody>
    </table>
  </section>
</main>
<script>
const data = {payload};
const bounds = {{ minLon: -80.6, maxLon: -74.7, minLat: 39.6, maxLat: 42.4 }};
const color = {{
  "Lower access burden": "var(--green)",
  "Moderate access burden": "var(--gold)",
  "High access burden": "var(--red)"
}};
function xy(lat, lon) {{
  const x = 85 + (lon - bounds.minLon) / (bounds.maxLon - bounds.minLon) * 590;
  const y = 455 - (lat - bounds.minLat) / (bounds.maxLat - bounds.minLat) * 350;
  return [x, y];
}}
function fmt(n) {{ return new Intl.NumberFormat("en-US").format(n); }}
function selectCounty(row) {{
  document.querySelectorAll(".county").forEach(el => el.classList.toggle("active", el.dataset.county === row.county));
  document.getElementById("detailCounty").textContent = row.county + " County";
  document.getElementById("detailIntro").textContent = row.county + " is classified as " + row.access_group.toLowerCase() + " in this prototype.";
  document.getElementById("detailType").textContent = row.type;
  document.getElementById("detailPop").textContent = fmt(row.population);
  document.getElementById("detailMiles").textContent = row.nearest_hospital_miles + " mi";
  document.getElementById("detailRate").textContent = row.hospitals_per_100k;
  document.getElementById("detailGroup").textContent = row.access_group;
  document.getElementById("detailNote").textContent = row.access_group === "High access burden"
    ? "Research implication: this county should be tested with real drive-time data, ambulance coverage, referral pathways, and telehealth availability."
    : "Research implication: supply alone is not enough; population pressure, insurance mix, specialty care, and travel time should be added next.";
  const maxMiles = Math.max(...data.counties.map(d => d.nearest_hospital_miles));
  const maxRate = Math.max(...data.counties.map(d => d.hospitals_per_100k));
  document.getElementById("bars").innerHTML = `
    <div class="bar-row"><span>Distance</span><div class="track"><div class="fill" style="width:${{Math.max(4, row.nearest_hospital_miles / maxMiles * 100)}}%; background:${{color[row.access_group]}}"></div></div><span>${{row.nearest_hospital_miles}} mi</span></div>
    <div class="bar-row"><span>Supply</span><div class="track"><div class="fill" style="width:${{Math.max(4, row.hospitals_per_100k / maxRate * 100)}}%; background:var(--blue)"></div></div><span>${{row.hospitals_per_100k}}</span></div>
  `;
}}
const countyLayer = document.getElementById("counties");
data.counties.forEach(row => {{
  const [x, y] = xy(row.lat, row.lon);
  const r = Math.max(9, Math.min(30, Math.sqrt(row.population) / 42));
  const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
  g.innerHTML = `<circle class="county" data-county="${{row.county}}" cx="${{x}}" cy="${{y}}" r="${{r}}" fill="${{color[row.access_group]}}" fill-opacity=".72" stroke="#17201b"></circle><text class="label" x="${{x + r + 4}}" y="${{y + 4}}">${{row.county}}</text>`;
  g.querySelector("circle").addEventListener("click", () => selectCounty(row));
  countyLayer.appendChild(g);
}});
const hospitalLayer = document.getElementById("hospitals");
data.hospitals.forEach(row => {{
  const [x, y] = xy(row.lat, row.lon);
  const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  c.setAttribute("class", "hospital");
  c.setAttribute("cx", x);
  c.setAttribute("cy", y);
  c.setAttribute("r", 5);
  hospitalLayer.appendChild(c);
}});
const sorted = [...data.counties].sort((a, b) => b.nearest_hospital_miles - a.nearest_hospital_miles);
document.getElementById("tableBody").innerHTML = sorted.map(row => `<tr><td>${{row.county}}</td><td>${{row.type}}</td><td>${{row.nearest_hospital_miles}}</td><td>${{row.hospitals_per_100k}}</td><td>${{row.access_group}}</td></tr>`).join("");
document.getElementById("highCount").textContent = data.counties.filter(d => d.access_group === "High access burden").length;
document.getElementById("avgDistance").textContent = (data.counties.reduce((s, d) => s + d.nearest_hospital_miles, 0) / data.counties.length).toFixed(1);
selectCounty(sorted[0]);
</script>
</body>
</html>
"""
    FIGURES.mkdir(exist_ok=True)
    (FIGURES / "interactive_hospital_access_map.html").write_text(html, encoding="utf-8")


def main():
    rows = build_metrics()
    write_csv(rows)
    write_readme(rows)
    write_pitch()
    write_email()
    write_html(rows)


if __name__ == "__main__":
    main()
