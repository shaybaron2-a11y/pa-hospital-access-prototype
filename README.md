# Pennsylvania Hospital Access Prototype

**Live entry point for GitHub Pages:** open `index.html`.

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
| Cameron | Rural | 48.0 | 0.0 | High access burden |
| Tioga | Rural | 38.3 | 0.0 | High access burden |
| Centre | College/rural | 0.0 | 0.63 | Moderate access burden |
| Lancaster | Small metro | 0.0 | 0.72 | Moderate access burden |
| Bucks | Suburban | 0.0 | 0.77 | Moderate access burden |

## Files

- `index.html`: GitHub Pages-ready visual portfolio page.
- `figures/interactive_hospital_access_map.html`: interactive map-style dashboard for professor outreach.
- `data/pa_county_access_prototype.csv`: county-level access metrics used by the dashboard.
- `data/pa_hospital_reference_points.csv`: hospital reference points used for nearest-distance calculations.
- `scripts/build_project.py`: reproducible script that generates the data, dashboard, and outreach materials.
- `DATA_SOURCES.md`: recommended official data sources and validation plan.
- `professor_email_template.md`: email template for contacting faculty.
- `one_page_project_pitch.md`: one-page project summary suitable for attaching to an email.

## Important note on data

This is a polished prototype, not a final peer-reviewed dataset. County populations, vulnerability variables, and hospital locations are simplified reference values used to demonstrate a research workflow. A stronger version should use:

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
