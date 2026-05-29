# Taipei MRT Retail Dynamics

## Retail and urban-commercial dynamics around Gongguan, Zhongxiao Fuxing, and Zhongshan MRT stations

This repository contains a reproducible Python data science project that compares retail and urban-commercial dynamics within 500 m catchments around three Taipei MRT stations:

- **Gongguan**: university, student, and food-service node
- **Zhongxiao Fuxing**: high-intensity transfer and premium retail node
- **Zhongshan**: shopping, culture, tourism, and lifestyle node

The project creates station buffers, collects OpenStreetMap POIs, classifies retail categories, compares station-area commercial mix, adds station-exit and walk-network sensitivity checks, and incorporates verified MRT passenger-flow data.

## Research question

How do retail density, retail mix, catchment definition, and MRT passenger flow differ across three Taipei MRT station areas?

The project uses a 500 m station catchment as the main analytical unit, while clearly separating verified metrics from proxy indicators.

## Repository contents

```text
taipei-mrt-retail-dynamics/
├── README.md
├── GITHUB_FINAL.md
├── requirements.txt
├── data/
│   ├── raw/
│   ├── processed/
│   └── outputs/
├── notebooks/
│   └── 01_mrt_retail_analysis.ipynb
├── scripts/
│   ├── 01_create_buffers.py
│   ├── 02_collect_osm_pois.py
│   ├── 03_analyze_retail_mix.py
│   ├── 04_make_maps_and_charts.py
│   ├── 05_generate_report.py
│   ├── 06_create_network_catchments.py
│   ├── 07_add_station_exits.py
│   ├── 08_passenger_flow_metric.py
│   ├── 09_make_validation_sample.py
│   └── 10_compare_catchment_methods.py
├── reports/
│   └── taipei_mrt_retail_dynamics_report.md
└── outputs/
    ├── buffers/
    ├── charts/
    ├── maps/
    └── tables/
```

## Data and metric status

| Data layer | Status | Use in project |
|---|---:|---|
| Station center coordinates | Verified project input | Creates baseline station points and 500 m circular buffers |
| EPSG:3826 projection | Verified method | Creates metric buffers in Taiwan TWD97 / TM2 zone 121 |
| OpenStreetMap POIs | Proxy metric | Estimates commercial density and retail mix |
| Taipei MRT station exits | Verified local source file | Creates exit-based catchment sensitivity check |
| Taipei Metro OD passenger flow | Verified local source file | Adds station-level passenger-flow comparison |
| Business opening/closure or turnover data | Not included | Requires transparent geocoding before use |
| Demographic, land-use, bus-stop, building-footprint data | Placeholder only | Future extension layers |

## Methodology

1. Create station point data from the three supplied coordinates.
2. Reproject station points from EPSG:4326 to EPSG:3826.
3. Create 500 m circular buffers.
4. Export combined and station-specific GeoJSON files.
5. Collect OpenStreetMap POIs within each catchment.
6. Classify POIs into retail categories:
   - food
   - cafe
   - convenience
   - apparel/fashion
   - lifestyle/design
   - education
   - health
   - services
   - other
7. Generate retail count and category-share comparison tables.
8. Generate charts and maps.
9. Add sensitivity checks using:
   - OSM walk-network catchments
   - official station-exit-based buffers
10. Add verified MRT passenger-flow totals.

The preferred method remains **buffer-first spatial joining**. All POI results should be interpreted as OSM-based proxy indicators, not as official business counts.

## Main maps and charts

### NCCU Innofest A1 poster

[Download the A1 poster PDF](outputs/poster/nccu_innofest_taipei_mrt_retail_dynamics_a1_poster.pdf)

![NCCU Innofest A1 poster preview](outputs/poster/nccu_innofest_taipei_mrt_retail_dynamics_a1_poster_preview.png)

### Combined POI map

![Combined POI map](outputs/maps/combined_poi_map.png)

### Catchment method comparison

![Catchment method comparison map](outputs/maps/catchment_method_comparison_map.png)

### Retail category mix

![Retail category count chart](outputs/charts/retail_category_count_by_station.png)

### Passenger flow

![MRT passenger flow chart](outputs/charts/mrt_passenger_flow_by_station.png)

## Key results

### Baseline 500 m circular catchment POI counts

| Station | OSM POIs |
|---|---:|
| Zhongshan | 867 |
| Gongguan | 732 |
| Zhongxiao Fuxing | 561 |

In the baseline circular-buffer analysis, Zhongshan has the highest observed OSM POI count, followed by Gongguan and Zhongxiao Fuxing.

### Retail category counts

| Station | Food | Cafe | Convenience | Apparel/fashion | Lifestyle/design | Education | Health | Services | Other |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Gongguan | 258 | 66 | 22 | 58 | 28 | 5 | 41 | 123 | 131 |
| Zhongshan | 325 | 78 | 34 | 79 | 22 | 3 | 30 | 160 | 136 |
| Zhongxiao Fuxing | 258 | 49 | 33 | 43 | 14 | 3 | 26 | 75 | 60 |

Food-related POIs are the largest category in all three station areas. This supports the idea that station-adjacent retail environments in central Taipei are strongly shaped by eating, drinking, and convenience-oriented activity.

### Catchment method sensitivity

| Catchment method | Gongguan | Zhongshan | Zhongxiao Fuxing |
|---|---:|---:|---:|
| Circular center 500 m | 733 | 869 | 561 |
| Exit-union 500 m | 789 | 1,076 | 641 |
| Walk-network 500 m | 613 | 635 | 409 |

The catchment definition changes the results. Exit-based buffers increase POI counts because multiple station exits expand the effective catchment footprint. Walk-network catchments reduce POI counts because they are constrained by the reachable pedestrian network rather than a full circle.

### Walk-network area comparison

| Station | Reachable OSM nodes | Network catchment area sqm | Circular area sqm | Network area as percent of circular |
|---|---:|---:|---:|---:|
| Gongguan | 637 | 414,689 | 784,137 | 52.9 |
| Zhongxiao Fuxing | 380 | 491,547 | 784,137 | 62.7 |
| Zhongshan | 631 | 511,001 | 784,137 | 65.2 |

The walk-network polygons are substantially smaller than the circular buffers, which shows why a simple radius can overstate reachable retail area.

### Station exits

| Station | Exit count |
|---|---:|
| Gongguan | 4 |
| Zhongshan | 6 |
| Zhongxiao Fuxing | 5 |

Station exits matter because they change where passengers enter the street network. For Zhongshan especially, the exit-union catchment captures a larger commercial footprint than the center-point buffer.

### March 2026 MRT passenger flow

| Station | Entries | Exits | Total station flow |
|---|---:|---:|---:|
| Zhongshan | 264,501 | 286,837 | 551,338 |
| Zhongxiao Fuxing | 234,498 | 244,744 | 479,242 |
| Gongguan | 161,390 | 163,588 | 324,978 |

Passenger flow is a verified MRT metric, but it is still only a proxy for retail foot traffic. It measures station usage, not actual spending, store visits, or pedestrian dwell time inside the 500 m catchment.

## Interpretation

Zhongshan has the largest baseline OSM POI count and the highest passenger-flow total among the three stations in the current data. Its profile fits the report framing of a shopping, culture, tourism, and lifestyle-oriented node.

Gongguan has a strong food and cafe profile and remains consistent with its student and university-oriented framing. Its passenger-flow total is lower than the other two stations, but its commercial density remains high within the baseline 500 m catchment.

Zhongxiao Fuxing has lower observed OSM POI counts than the other two stations in this specific 500 m analysis, but it has high verified passenger flow. This suggests that its role as a transfer and premium retail node may not be fully captured by simple POI counts alone. Store size, department stores, underground retail, vertical malls, and higher-value commercial activity require additional datasets.

## Limitations

- OSM POIs are not official business records.
- OSM completeness varies by area and by tag.
- A circular 500 m buffer does not model pedestrian barriers, exits, underground passages, or actual walking paths.
- The walk-network catchment uses an approximate convex-hull service area from reachable OSM nodes, not a full network-service polygon.
- POI counts do not measure sales, rent, vacancy, store size, turnover, or customer volume.
- MRT passenger flow measures station entries and exits, not retail visits.
- Business turnover/opening/closure data was not added because reliable geocoding was not implemented.
- Demographic, land-use, bus-stop, and building-footprint layers are placeholders for future extension.

## How to reproduce

Create the Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the full workflow:

```bash
python scripts/01_create_buffers.py
python scripts/02_collect_osm_pois.py
python scripts/03_analyze_retail_mix.py
python scripts/06_create_network_catchments.py
python scripts/07_add_station_exits.py
python scripts/08_passenger_flow_metric.py
python scripts/09_make_validation_sample.py
python scripts/10_compare_catchment_methods.py
python scripts/04_make_maps_and_charts.py
python scripts/05_generate_report.py
```

The OSM scripts require internet access because they query OpenStreetMap through OSMnx.

## Important output files

### Reports

- [Final Markdown report](reports/taipei_mrt_retail_dynamics_report.md)
- [Notebook workflow](notebooks/01_mrt_retail_analysis.ipynb)
- [NCCU Innofest A1 poster PDF](outputs/poster/nccu_innofest_taipei_mrt_retail_dynamics_a1_poster.pdf)
- [Poster generator script](scripts/11_generate_innofest_poster.py)

### Spatial outputs

- [Combined circular 500 m buffers](outputs/buffers/mrt_station_500m_buffers.geojson)
- [Walk-network catchments](outputs/buffers/mrt_station_500m_walk_network_catchments.geojson)
- [Exit-based buffers](outputs/buffers/mrt_exit_based_500m_buffers.geojson)
- [Station points](data/processed/mrt_station_points.geojson)
- [Station exits](data/processed/mrt_station_exits.geojson)

### Tables

- [Total POI count by station](outputs/tables/total_poi_count_by_station.csv)
- [Retail category counts](outputs/tables/retail_category_count_by_station.csv)
- [Retail category shares](outputs/tables/retail_category_share_by_station.csv)
- [Catchment method POI comparison](outputs/tables/catchment_method_total_poi_comparison.csv)
- [Catchment method category comparison](outputs/tables/catchment_method_category_comparison.csv)
- [Passenger flow by station](outputs/tables/mrt_passenger_flow_by_station.csv)
- [Manual OSM validation sample](outputs/tables/manual_osm_category_validation_sample.csv)
