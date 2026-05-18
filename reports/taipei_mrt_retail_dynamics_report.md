# Taipei MRT Retail Dynamics Around Gongguan, Zhongxiao Fuxing, and Zhongshan

Generated: 2026-05-18

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

OSM collection status: OSM POI collection completed successfully with 2160 POIs.

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

## Comparative station analysis

### Total OSM POI count by station

| station_id       | station_name     |   total_osm_pois |
|:-----------------|:-----------------|-----------------:|
| zhongshan        | Zhongshan        |              867 |
| gongguan         | Gongguan         |              732 |
| zhongxiao_fuxing | Zhongxiao Fuxing |              561 |

### Retail category count by station

| station_id       | station_name     |   food |   cafe |   convenience |   apparel/fashion |   lifestyle/design |   education |   health |   services |   other |
|:-----------------|:-----------------|-------:|-------:|--------------:|------------------:|-------------------:|------------:|---------:|-----------:|--------:|
| gongguan         | Gongguan         |    258 |     66 |            22 |                58 |                 28 |           5 |       41 |        123 |     131 |
| zhongshan        | Zhongshan        |    325 |     78 |            34 |                79 |                 22 |           3 |       30 |        160 |     136 |
| zhongxiao_fuxing | Zhongxiao Fuxing |    258 |     49 |            33 |                43 |                 14 |           3 |       26 |         75 |      60 |

### Retail category share by station

| station_id       | station_name     |   food |   cafe |   convenience |   apparel/fashion |   lifestyle/design |   education |   health |   services |   other |
|:-----------------|:-----------------|-------:|-------:|--------------:|------------------:|-------------------:|------------:|---------:|-----------:|--------:|
| gongguan         | Gongguan         | 0.3525 | 0.0902 |        0.0301 |            0.0792 |             0.0383 |      0.0068 |   0.056  |     0.168  |  0.179  |
| zhongshan        | Zhongshan        | 0.3749 | 0.09   |        0.0392 |            0.0911 |             0.0254 |      0.0035 |   0.0346 |     0.1845 |  0.1569 |
| zhongxiao_fuxing | Zhongxiao Fuxing | 0.4599 | 0.0873 |        0.0588 |            0.0766 |             0.025  |      0.0053 |   0.0463 |     0.1337 |  0.107  |

## Catchment method sensitivity

The baseline method uses one 500 m circular buffer from each station center. Two sensitivity checks were added: a 500 m walk-network catchment and a 500 m dissolved exit-based buffer. These are useful because station exits and pedestrian networks can shift the effective commercial catchment.

### Catchment area comparison

| station_id       | station_name     |   reachable_node_count |   network_catchment_area_sqm |   circular_buffer_area_sqm |   network_area_pct_of_circular |
|:-----------------|:-----------------|-----------------------:|-----------------------------:|---------------------------:|-------------------------------:|
| gongguan         | Gongguan         |                    637 |                       414689 |                     784137 |                           52.9 |
| zhongxiao_fuxing | Zhongxiao Fuxing |                    380 |                       491547 |                     784137 |                           62.7 |
| zhongshan        | Zhongshan        |                    631 |                       511001 |                     784137 |                           65.2 |

### Total OSM POI count by catchment method

| catchment_method     | station_id       | station_name     |   total_osm_pois |
|:---------------------|:-----------------|:-----------------|-----------------:|
| circular_center_500m | gongguan         | Gongguan         |              733 |
| circular_center_500m | zhongshan        | Zhongshan        |              869 |
| circular_center_500m | zhongxiao_fuxing | Zhongxiao Fuxing |              561 |
| exit_union_500m      | gongguan         | Gongguan         |              789 |
| exit_union_500m      | zhongshan        | Zhongshan        |             1076 |
| exit_union_500m      | zhongxiao_fuxing | Zhongxiao Fuxing |              641 |
| walk_network_500m    | gongguan         | Gongguan         |              613 |
| walk_network_500m    | zhongshan        | Zhongshan        |              635 |
| walk_network_500m    | zhongxiao_fuxing | Zhongxiao Fuxing |              409 |

### Retail category count by catchment method

| catchment_method     | station_id       | station_name     |   apparel/fashion |   cafe |   convenience |   education |   food |   health |   lifestyle/design |   other |   services |
|:---------------------|:-----------------|:-----------------|------------------:|-------:|--------------:|------------:|-------:|---------:|-------------------:|--------:|-----------:|
| circular_center_500m | gongguan         | Gongguan         |                58 |     66 |            22 |           6 |    258 |       41 |                 28 |     131 |        123 |
| circular_center_500m | zhongshan        | Zhongshan        |                80 |     78 |            34 |           3 |    325 |       30 |                 22 |     137 |        160 |
| circular_center_500m | zhongxiao_fuxing | Zhongxiao Fuxing |                43 |     49 |            33 |           3 |    258 |       26 |                 14 |      60 |         75 |
| exit_union_500m      | gongguan         | Gongguan         |                61 |     69 |            24 |           7 |    282 |       43 |                 30 |     136 |        137 |
| exit_union_500m      | zhongshan        | Zhongshan        |                94 |     92 |            48 |           4 |    392 |       45 |                 33 |     171 |        197 |
| exit_union_500m      | zhongxiao_fuxing | Zhongxiao Fuxing |                56 |     54 |            37 |           4 |    280 |       28 |                 15 |      72 |         95 |
| walk_network_500m    | gongguan         | Gongguan         |                52 |     51 |            18 |           4 |    232 |       33 |                 23 |     120 |         80 |
| walk_network_500m    | zhongshan        | Zhongshan        |                68 |     60 |            20 |           3 |    229 |       25 |                 17 |     105 |        108 |
| walk_network_500m    | zhongxiao_fuxing | Zhongxiao Fuxing |                41 |     28 |            26 |           1 |    172 |       21 |                 13 |      52 |         55 |

## Station exits

| station_id       | station_name     |   exit_count |
|:-----------------|:-----------------|-------------:|
| gongguan         | Gongguan         |            4 |
| zhongshan        | Zhongshan        |            6 |
| zhongxiao_fuxing | Zhongxiao Fuxing |            5 |

The station-exit layer is treated as a verified spatial input from the local Taipei MRT exit coordinate file. Exit-based catchments should be interpreted as a sensitivity test, not as a replacement for pedestrian network analysis.

## Passenger flow

| station_id       | station_name     | station_name_zh   | month   | verified_metric                |   entries |   exits |   total_station_flow | source_file                                                                                 |
|:-----------------|:-----------------|:------------------|:--------|:-------------------------------|----------:|--------:|---------------------:|:--------------------------------------------------------------------------------------------|
| zhongshan        | Zhongshan        | 中山              | 2026-03 | Taipei Metro OD passenger flow |    264501 |  286837 |               551338 | /Users/konstantin/Documents/Playground/retail_vacancy_prediction/data/raw/mrt_od_latest.csv |
| zhongxiao_fuxing | Zhongxiao Fuxing | 忠孝復興          | 2026-03 | Taipei Metro OD passenger flow |    234498 |  244744 |               479242 | /Users/konstantin/Documents/Playground/retail_vacancy_prediction/data/raw/mrt_od_latest.csv |
| gongguan         | Gongguan         | 公館              | 2026-03 | Taipei Metro OD passenger flow |    161390 |  163588 |               324978 | /Users/konstantin/Documents/Playground/retail_vacancy_prediction/data/raw/mrt_od_latest.csv |

Passenger flow is a verified metric from the Taipei Metro OD file used here, aggregated as station entries plus station exits. It is still a proxy for nearby commercial foot traffic because not every station passenger becomes a retail pedestrian inside the 500 m catchment.

## Manual validation sample

A manual category-check sample was exported to `outputs/tables/manual_osm_category_validation_sample.csv`. This file should be checked against OSM, Google Maps, or field knowledge by filling in the `manual_category_check` and `manual_notes` columns.

## Findings

The core interpretation should focus on differences in observed POI density and category mix across the three buffers. Gongguan is expected to show strong food, cafe, convenience, and education-related activity because of its student-oriented context. Zhongxiao Fuxing is expected to show a higher-intensity commercial profile with more premium retail and service activity because it is a major transfer and shopping node. Zhongshan is expected to show a mixed shopping, culture, tourism, and lifestyle profile.

These findings should be read as OSM-based indicators rather than final ground truth. If the POI tables are empty or incomplete, rerun the OSM collection step with internet access and current package versions.

## Limitations

- OpenStreetMap completeness varies by neighborhood and tagging behavior.
- A 500 m circular buffer is simple and reproducible, but it does not model pedestrian network distance, barriers, street connectivity, or station exits.
- POI counts do not measure revenue, vacancy, rent, foot traffic, store size, or business turnover.
- Category classification is rule-based and may misclassify ambiguous OSM tags.
- District-level demographic indicators should not be treated as final evidence for station-level catchments.
- This version does not include village-level demographics, land-use polygons, bus stops, building footprints, storefront vacancy records, or official business opening/closure records.
- Business turnover/opening/closure data was not added because reliable address matching and geocoding were not implemented in this pass. Adding it without transparent geocoding would create false precision.

## Placeholder datasets for future extension

Village-level demographic data should be added as a spatial layer and intersected with the 500 m buffers only if the geometry and date are documented.

Land-use polygons should be added to estimate the share of commercial, residential, institutional, and mixed-use land inside each catchment.

Bus stops and transfer facilities should be added to improve the interpretation of multimodal access and commercial intensity.

Building footprints should be added to estimate built-form density and ground-floor commercial potential.

Official business registration, opening, and closure records should be added only if address matching or geocoding is transparent enough to avoid false precision.

## Next steps

1. Replace convex-hull walk-network catchments with true network-service polygons if a more precise service-area method is needed.
2. Add official business turnover or opening/closure data only after building a transparent geocoding workflow.
3. Fill in the manual validation sample and revise the OSM category rules where misclassifications appear.
4. Add village-level demographics, land-use, bus-stop, and building-footprint layers if source files are available.
