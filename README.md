# Pennsylvania Hospital Access Prototype

Interactive GitHub Pages dashboard for exploring spatial inequality in hospital access across Pennsylvania.

## What changed

The dashboard now uses a reproducible official-data snapshot instead of the original 12-county demonstration values. It includes all 67 Pennsylvania counties and 109 geocoded CMS acute-care hospital records retrieved on 2026-08-22.

Interactive features include:

- county search and population-band/access-group filters;
- synchronized map, scatterplot, detail panel, and comparison table;
- map color modes for access group, priority, distance, and hospital supply;
- selectable county records with metric bars and per-record source links;
- visible-row CSV export;
- keyboard-accessible map and chart markers;
- explicit provenance and limitations for original versus derived metrics.

## Run locally

The page is static and can be opened directly as `index.html`. To rebuild the official snapshot:

```powershell
python scripts/fetch_official_data.py
```

The script writes:

- `data/pa_access_official.js`: page-ready JSON snapshot;
- `data/pa_county_access_official.csv`: county metrics and source fields;
- `data/pa_hospitals_official.csv`: CMS hospital records and geocoded coordinates;
- `data/pa_access_metadata.json`: source registry and retrieval date.

## Research question

Which Pennsylvania counties appear to have weaker geographic access to acute-care hospitals, and how could a stronger study connect these patterns to transportation, referral networks, telehealth, and hospital-system planning?

## Methods

The current snapshot uses ACS population and vulnerability estimates, CMS Hospital General Information records, Census TIGERweb county boundaries, and Census Geocoder address coordinates. The page derives centroid-to-hospital great-circle distance, acute-care hospitals per 100,000 residents, a population-threshold band, and an exploratory priority score.

## Important limitations

This is a research prototype, not a validated policy or clinical model. The distance metric is straight-line distance from a county polygon centroid, not drive time. Hospital count does not represent beds, specialty capacity, quality, or referral availability. ACS release vintage is retained per county and may be 1-year or 5-year depending on the returned official release. See [`DATA_SOURCES.md`](DATA_SOURCES.md) for the source registry and validation plan.
