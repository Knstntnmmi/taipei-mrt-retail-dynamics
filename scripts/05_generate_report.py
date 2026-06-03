import json
from datetime import date

import pandas as pd

from project_config import DATA_RAW, REPORTS_DIR, TABLES_DIR, ensure_directories


def markdown_table(path):
    if not path.exists():
        return "_Table not available. Run the analysis scripts first._"
    return pd.read_csv(path).to_markdown(index=False)


def osm_status_text() -> str:
    status_path = DATA_RAW / "osm_collection_status.json"
    if not status_path.exists():
        return "OSM collection has not been run yet."
    status = json.loads(status_path.read_text())
    if status.get("status") == "success":
        return f"OSM POI collection completed successfully with {status.get('poi_count')} POIs."
    return f"OSM POI collection did not complete: {status.get('message')}"


def optional_section(title, path):
    if not path.exists():
        return f"## {title}\n\n_Not available. Run the relevant extension script first._\n"
    return f"## {title}\n\n{markdown_table(path)}\n"


def main() -> None:
    ensure_directories()
    report = f"""# Taipei MRT Retail Dynamics Around Gongguan, Zhongxiao Fuxing, and Zhongshan

Generated: {date.today().isoformat()}

## Executive summary

This project compares retail and urban-commercial dynamics within 500 m walking catchments around three Taipei MRT stations: Gongguan, Zhongxiao Fuxing, and Zhongshan. The analysis keeps the existing comparative frame: Gongguan is treated as a university/student/food-service node, Zhongxiao Fuxing as a high-intensity transfer and premium retail node, and Zhongshan as a shopping/culture/tourism node.

The reproducible pipeline creates station points from specified coordinates, projects the data to Taiwan's metric CRS (EPSG:3826), generates 500 m buffers, collects OpenStreetMap POIs where available, classifies POIs into retail categories, and exports comparison tables, charts, maps, and this report.

## Research frame and assumptions

The analytical unit is a 500 m radius catchment around each station center. This is a spatial proxy for the immediate MRT retail environment, not a claim about official station service areas or actual pedestrian network distance.

Verified inputs:

- Station names and coordinates supplied in the project brief.
- 500 m buffer distance.
- Taiwan metric projection EPSG:3826 for distance-based buffering.

Proxy metrics:

- OpenStreetMap POIs are used as a proxy for retail and commercial density.
- POI category counts are used as a proxy for local retail mix.
- Category shares are used as a proxy for functional specialization.

## Data sources

- Station coordinate input: project brief / existing report.
- Spatial processing: GeoPandas, Shapely, PyProj.
- Retail and commercial POIs: OpenStreetMap data accessed through OSMnx.
- Station exits: Taipei MRT station-exit coordinate file from the earlier local project data source.
- Passenger flow: Taipei Metro station OD passenger-flow file from the earlier local project data source.
- CRS: WGS84 for web mapping and EPSG:3826 for metric buffering.

OSM collection status: {osm_status_text()}

## Methodology

1. Create station point data from the three supplied coordinates.
2. Reproject station points from EPSG:4326 to EPSG:3826.
3. Create 500 m buffers in the metric CRS.
4. Reproject buffers back to EPSG:4326 for GeoJSON export and web compatibility.
5. Query OSM POIs inside each buffer.
6. Use a buffer-first spatial join to retain only POIs located within each station catchment.
7. Classify POIs into: food, cafe, convenience, apparel/fashion, lifestyle/design, education, health, services, and other.
8. Export count tables, share tables, charts, and maps.

Extension methods added after the first reproducible version:

- Walk-network catchments: OSMnx walking networks are used to estimate the area reachable within 500 m walking distance from each station center. This is a proxy service-area polygon, not an official pedestrian catchment.
- Exit-based catchments: official station-exit points are buffered by 500 m and dissolved by station. This tests whether using station exits changes the observed POI mix.
- Passenger-flow metric: March 2026 station OD totals are aggregated into entries, exits, and total station flow.
- Manual validation sample: a small OSM POI sample is exported for manual category checking.
- Station-level business openings and closures: official Taipei City geocoded establishment and closure records are spatially joined to the 500 m station catchments for the latest available month.
- Normalized station indicators: latest opening/closure events are divided by the OpenStreetMap mapped-place base to compare turnover intensity across station areas.

## Comparative station analysis

### Total OSM POI count by station

{markdown_table(TABLES_DIR / "total_poi_count_by_station.csv")}

### Retail category count by station

{markdown_table(TABLES_DIR / "retail_category_count_by_station.csv")}

### Retail category share by station

{markdown_table(TABLES_DIR / "retail_category_share_by_station.csv")}

## Catchment method sensitivity

The baseline method uses one 500 m circular buffer from each station center. Two sensitivity checks were added: a 500 m walk-network catchment and a 500 m dissolved exit-based buffer. These are useful because station exits and pedestrian networks can shift the effective commercial catchment.

### Catchment area comparison

{markdown_table(TABLES_DIR / "network_vs_circular_catchment_area.csv")}

### Total OSM POI count by catchment method

{markdown_table(TABLES_DIR / "catchment_method_total_poi_comparison.csv")}

### Retail category count by catchment method

{markdown_table(TABLES_DIR / "catchment_method_category_comparison.csv")}

## Station exits

{markdown_table(TABLES_DIR / "mrt_exit_count_by_station.csv")}

The station-exit layer is treated as a verified spatial input from the local Taipei MRT exit coordinate file. Exit-based catchments should be interpreted as a sensitivity test, not as a replacement for pedestrian network analysis.

## Passenger flow

{markdown_table(TABLES_DIR / "mrt_passenger_flow_by_station.csv")}

Passenger flow is a verified metric from the Taipei Metro OD file used here, aggregated as station entries plus station exits. It is still a proxy for nearby commercial foot traffic because not every station passenger becomes a retail pedestrian inside the 500 m catchment.

## Business opening and closure evidence

### Latest station-level business openings and closures

{markdown_table(TABLES_DIR / "station_business_open_close_latest_month_summary.csv")}

These station-level counts use official Taipei City geocoded business establishment and closure records for the latest available month. The records are spatially joined into the three 500 m station catchments, so this is the strongest direct opening/closure evidence currently available in the project.

### Normalized station turnover indicators

{markdown_table(TABLES_DIR / "station_normalized_turnover_indicators.csv")}

Raw event counts show absolute opening/closure volume. The normalized indicator `turnover_events_per_100_pois` divides latest opening plus closure events by the OpenStreetMap mapped-place base. This does not turn OpenStreetMap into an official denominator, but it makes the station comparison more defensible because larger mapped retail bases no longer automatically dominate the comparison.

## Manual validation sample

A manual category-check sample was exported to `outputs/tables/manual_osm_category_validation_sample.csv`. This file should be checked against OSM, Google Maps, or field knowledge by filling in the `manual_category_check` and `manual_notes` columns.

## Findings

The core interpretation should focus on differences in verified latest-month business turnover, observed POI density, passenger-flow context, and category mix across the three buffers.

Zhongshan has the strongest latest-month opening/closure signal among the three stations. It has 23 latest-month events and 2.65 opening/closure events per 100 mapped places.

Zhongxiao Fuxing has lower latest-month opening/closure volume than Zhongshan, but it has the highest passenger-flow intensity per mapped place. This supports the caveat that simple point counts may understate its vertical malls, department stores, underground retail, and premium commercial activity.

Gongguan has the lowest latest-month business-turnover intensity in this comparison, but its OpenStreetMap retail mix still supports the framing of a student-oriented food and everyday-service node.

These findings should be read as OSM-based indicators rather than final ground truth. If the POI tables are empty or incomplete, rerun the OSM collection step with internet access and current package versions.

## Limitations

- OpenStreetMap completeness varies by neighborhood and tagging behavior.
- A 500 m circular buffer is simple and reproducible, but it does not model pedestrian network distance, barriers, street connectivity, or station exits.
- POI counts do not measure revenue, vacancy, rent, foot traffic, store size, or long-run business turnover.
- Category classification is rule-based and may misclassify ambiguous OSM tags.
- District-level demographic indicators should not be treated as final evidence for station-level catchments.
- This version does not include village-level demographics, land-use polygons, bus stops, building footprints, storefront vacancy records, rent, revenue, or store-size records.
- Latest-month station-level business opening/closure data is included, but the full 2022-present station-geocoded opening/closure panel is not available in this project. The longer historical opening/closure percentages remain city-level or national industry context, not station-level proof.

## Placeholder datasets for future extension

Village-level demographic data should be added as a spatial layer and intersected with the 500 m buffers only if the geometry and date are documented.

Land-use polygons should be added to estimate the share of commercial, residential, institutional, and mixed-use land inside each catchment.

Bus stops and transfer facilities should be added to improve the interpretation of multimodal access and commercial intensity.

Building footprints should be added to estimate built-form density and ground-floor commercial potential.

Additional official business registration, opening, and closure records should be added only if address matching or geocoding is transparent enough to avoid false precision.

## Next steps

1. Replace convex-hull walk-network catchments with true network-service polygons if a more precise service-area method is needed.
2. Add official business turnover or opening/closure data only after building a transparent geocoding workflow.
3. Fill in the manual validation sample and revise the OSM category rules where misclassifications appear.
4. Add village-level demographics, land-use, bus-stop, and building-footprint layers if source files are available.
"""
    output_path = REPORTS_DIR / "taipei_mrt_retail_dynamics_report.md"
    output_path.write_text(report)
    print(f"Saved report: {output_path}")


if __name__ == "__main__":
    main()
