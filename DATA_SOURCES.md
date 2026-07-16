# Data sources and next-step validation plan

This repository is a polished research prototype. The current county sample is intentionally labeled as preliminary because it is meant for faculty outreach and method demonstration, not final policy inference.

## Current prototype inputs

- County reference points: simplified county centroid/reference coordinates for selected Pennsylvania counties.
- Hospital reference points: simplified hospital-market or regional hospital cluster points.
- Population and vulnerability variables: approximate county profile values used to demonstrate a multi-variable access-burden framework.

## Recommended official sources for the next version

- **U.S. Census Bureau ACS 5-year estimates:** population, age structure, poverty, uninsured status, income, race/ethnicity, and commuting variables at county, tract, or block-group level.
- **CMS Provider Data / Care Compare:** hospital facility-level information, ownership, ratings, emergency services, and quality indicators.
- **HIFLD Hospitals:** geocoded facility locations for hospitals and emergency care infrastructure.
- **TIGER/Line shapefiles:** official Census geographic boundaries for Pennsylvania counties and census tracts.
- **Road-network travel time:** ArcGIS Network Analyst, OpenRouteService, OSRM, or another routing engine to replace straight-line distance.

## Academic upgrade path

1. Replace county centroids with tract-level population-weighted centroids.
2. Replace simplified hospital points with verified CMS/HIFLD facility locations.
3. Filter hospitals by emergency-service availability and facility type.
4. Calculate 15-, 30-, 45-, and 60-minute drive-time catchments.
5. Add social vulnerability variables from ACS.
6. Estimate population-weighted access burden and compare rural/suburban/urban counties.
7. Validate findings against hospital referral regions or EMS service areas.

## How to describe this project honestly

Suggested wording:

> I built a prototype spatial-analysis workflow for studying hospital access in Pennsylvania. It is not a final empirical study yet; I am using it to show my research direction and to seek faculty guidance on upgrading it with official ACS, CMS/HIFLD, and drive-time data.

