import json

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
from shapely.geometry import MultiPoint

from project_config import (
    BUFFERS_DIR,
    DATA_RAW,
    NETWORK_BUFFER_METERS,
    STATIONS,
    TABLES_DIR,
    WGS84_CRS,
    ensure_directories,
)


def reachable_nodes_polygon(station):
    graph = ox.graph_from_point(
        (station["lat"], station["lon"]),
        dist=NETWORK_BUFFER_METERS + 200,
        network_type="walk",
        simplify=True,
    )
    center_node = ox.distance.nearest_nodes(graph, station["lon"], station["lat"])
    lengths = nx.single_source_dijkstra_path_length(
        graph,
        center_node,
        cutoff=NETWORK_BUFFER_METERS,
        weight="length",
    )
    nodes = ox.graph_to_gdfs(graph, edges=False)
    reachable = nodes.loc[list(lengths.keys())].copy()
    points = list(reachable.geometry)

    if len(points) < 3:
        polygon = MultiPoint(points).buffer(0.002)
    else:
        polygon = MultiPoint(points).convex_hull

    return polygon, len(reachable)


def main() -> None:
    ensure_directories()
    records = []

    try:
        for station in STATIONS:
            print(f"Creating walk-network catchment for {station['station_name']}...")
            polygon, node_count = reachable_nodes_polygon(station)
            records.append(
                {
                    **station,
                    "network_distance_m": NETWORK_BUFFER_METERS,
                    "reachable_node_count": node_count,
                    "geometry": polygon,
                }
            )
    except Exception as exc:
        (DATA_RAW / "network_catchment_status.json").write_text(
            json.dumps({"status": "failed", "message": str(exc)}, indent=2)
        )
        raise

    catchments = gpd.GeoDataFrame(records, geometry="geometry", crs=WGS84_CRS)
    catchments.to_file(BUFFERS_DIR / "mrt_station_500m_walk_network_catchments.geojson", driver="GeoJSON")

    circular = gpd.read_file(BUFFERS_DIR / "mrt_station_500m_buffers.geojson").to_crs(WGS84_CRS)
    comparison = catchments.to_crs("EPSG:3826")[["station_id", "station_name", "reachable_node_count", "geometry"]].copy()
    comparison["network_catchment_area_sqm"] = comparison.geometry.area.round(1)
    circular_metric = circular.to_crs("EPSG:3826")[["station_id", "geometry"]].copy()
    circular_metric["circular_buffer_area_sqm"] = circular_metric.geometry.area.round(1)
    comparison = comparison.drop(columns="geometry").merge(
        circular_metric[["station_id", "circular_buffer_area_sqm"]],
        on="station_id",
        how="left",
    )
    comparison["network_area_pct_of_circular"] = (
        comparison["network_catchment_area_sqm"] / comparison["circular_buffer_area_sqm"] * 100
    ).round(1)
    comparison.to_csv(TABLES_DIR / "network_vs_circular_catchment_area.csv", index=False)

    (DATA_RAW / "network_catchment_status.json").write_text(
        json.dumps({"status": "success", "station_count": len(catchments)}, indent=2)
    )
    print("Saved walk-network catchments and area comparison.")


if __name__ == "__main__":
    main()
