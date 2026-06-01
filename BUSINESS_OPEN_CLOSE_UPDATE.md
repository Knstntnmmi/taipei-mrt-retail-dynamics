# Business Opening and Closing Dynamics Update

This update adds the professor-requested opening/closing component to the Taipei MRT retail dynamics project.

## What changed

The project now includes official business-registration opening and closing metrics from 2022 through the latest available official update. These metrics are kept separate from the station-buffer OpenStreetMap POI counts because the official business-registration data is not geocoded to the 500 m MRT station catchments in this version.

## Data sources

- Taipei City annual business registrations by industry: https://data.gov.tw/dataset/131242
- Ministry of Economic Affairs / GCIS monthly business-registration industry data: https://data.gcis.nat.gov.tw/od/detail?oid=DB0B8C8F-9C1A-406F-8760-F7EA18942269

## Time coverage

- Taipei city-level annual industry data: 2022-2025
- GCIS monthly industry data: 2022-01 through 2026-04, latest available during the update

Important: the Taipei annual dataset is city-level and industry-level. The GCIS monthly dataset extends the trend through the latest available month, but it is national-level by industry. It is used only as current-period context, not as station-level evidence.

## Taipei city-level opening/closing percentages, 2022-2025

| Category | Openings | Closures | Opening share | Closure share | Closure rate of events |
|---|---:|---:|---:|---:|---:|
| Shop/retail | 9,107 | 8,793 | 46.34% | 49.98% | 49.12% |
| Food/cafe | 4,106 | 3,708 | 20.89% | 21.08% | 47.45% |
| Services | 1,960 | 1,492 | 9.97% | 8.48% | 43.22% |
| Lifestyle/culture | 1,427 | 1,007 | 7.26% | 5.72% | 41.37% |
| Education | 169 | 68 | 0.86% | 0.39% | 28.69% |
| Health | 0 | 0 | 0.00% | 0.00% | 0.00% |

## Main interpretation

Shop/retail and food/cafe dominate both openings and closures in Taipei's official city-level business-registration data. Together, they account for 67.23% of openings and 71.06% of closures from 2022-2025.

This strengthens the project argument: Taipei MRT station-area retail environments should be treated as dynamic commercial systems, not just static POI maps. The OSM station-buffer data shows what is currently visible around each station, while the official registration data shows broader opening/closing pressure in the business categories most relevant to shops, cafes, restaurants, and services.

## Methodological limitation

This update does not claim that these official opening/closing percentages occurred inside the 500 m buffers around Gongguan, Zhongxiao Fuxing, or Zhongshan. That would require address-level geocoding and spatial joining. The present version uses official city/industry and monthly industry data as contextual evidence alongside the station-level spatial analysis.
