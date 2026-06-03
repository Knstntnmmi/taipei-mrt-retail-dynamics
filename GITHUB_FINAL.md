# Taipei MRT Retail Dynamics

This repository is the final GitHub-facing version of the Taipei MRT retail dynamics project. The analysis focuses on business openings and closures around three MRT station areas using 500 m catchments:

- Gongguan: student food node
- Zhongxiao Fuxing: transfer and premium retail node
- Zhongshan: shopping, culture, and tourism node

## Front-Page Visual

The main GitHub visual is a smooth looping animation focused on station-level business activity around the three MRT stations:

![Animated station-by-station MRT retail dynamics loop](outputs/charts/mrt_station_retail_dynamics_loop.gif)

It shows each station's:

- 500 m catchment map
- mapped retail and service places from OpenStreetMap
- retail category mix
- March 2026 Taipei Metro passenger flow
- latest official Taipei City station-level business openings and closures
- comparison against the other two stations

## Main Evidence

| Station | Current mapped places | March 2026 station flow | Latest station-level business events |
|---|---:|---:|---:|
| Gongguan | 732 | 324,978 | +2 openings / -1 closure |
| Zhongxiao Fuxing | 561 | 479,242 | +3 openings / -2 closures |
| Zhongshan | 867 | 551,338 | +12 openings / -11 closures |

Zhongshan has the highest latest-month opening/closure volume among the three catchments. Gongguan and Zhongxiao Fuxing have lower latest-month turnover counts but still show both openings and closures inside the 500 m station areas.

## Normalized Evidence

Raw event counts are now paired with derived normalized indicators:

| Station | Events per 100 mapped places | Passenger flow per mapped place | Share of latest events |
|---|---:|---:|---:|
| Zhongshan | 2.65 | 635.9 | 74.19% |
| Zhongxiao Fuxing | 0.89 | 854.3 | 16.13% |
| Gongguan | 0.41 | 444.0 | 9.68% |

This makes the comparison more defensible. Zhongshan still has the strongest latest-month turnover signal after normalizing by the mapped retail base. Zhongxiao Fuxing shows the highest passenger-flow intensity per mapped place, which supports the caveat that point-of-interest counts may understate vertical and underground retail.

## Data-Science Argument

The project is framed as a reproducible claim-evidence-limitation analysis:

- Claim: Zhongshan shows the strongest latest-month business-turnover signal.
- Evidence: official Taipei City geocoded April 2026 opening and closure records inside each 500 m station catchment.
- Context: OpenStreetMap retail mix and Taipei Metro passenger flow explain each station area's commercial profile.
- Limitation: longer 2022-present opening/closure percentages remain city-level context, not station-level proof.
- Next data need: a full station-geocoded 2022-present business-event panel.

## Important Method Note

The project separates verified metrics from proxy metrics:

- Station coordinates, 500 m buffers, station exits, and Taipei Metro passenger flow are verified project inputs or official data.
- OpenStreetMap points of interest are proxy data for the visible commercial mix around each station.
- Latest Taipei City business establishment and closure records are geocoded and are spatially joined into the three station catchments.
- Longer 2022-present opening and closure percentages are still city-level industry context, because the full historical business-event panel is not yet available as clean geocoded station-level records.

## Reproducibility

The repository includes scripts, data tables, maps, charts, a notebook, and the final report. The main README explains how to rerun the full workflow.
