import importlib.util

import geopandas as gpd
import osmnx as ox
import pandas as pd

from project_config import BUFFERS_DIR, DATA_RAW, TABLES_DIR, WGS84_CRS, ensure_directories


def load_poi_helpers():
    helper_path = __file__.replace("10_compare_catchment_methods.py", "02_collect_osm_pois.py")
    spec = importlib.util.spec_from_file_location("collect_osm_pois", helper_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.OSM_TAGS, module.classify_poi, module.best_name


def collect_pois_for_catchments(catchments: gpd.GeoDataFrame, method_name: str) -> gpd.GeoDataFrame:
    osm_tags, classify_poi, best_name = load_poi_helpers()
    all_rows = []

    for _, row in catchments.iterrows():
        print(f"Collecting {method_name} POIs for {row['station_name']}...")
        pois = ox.features_from_polygon(row.geometry, tags=osm_tags)
        if pois.empty:
            continue
        pois = pois.reset_index()
        pois = pois[pois.geometry.notna()].copy()
        pois = pois[pois.geometry.geom_type.isin(["Point", "Polygon", "MultiPolygon"])].copy()
        pois["geometry"] = pois.geometry.representative_point()
        pois["station_id"] = row["station_id"]
        pois["station_name"] = row["station_name"]
        pois["catchment_method"] = method_name
        pois["poi_name"] = pois.apply(best_name, axis=1)
        pois["retail_category"] = pois.apply(classify_poi, axis=1)
        all_rows.append(pois)

    if not all_rows:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs=WGS84_CRS)

    combined = pd.concat(all_rows, ignore_index=True)
    keep = [
        "station_id",
        "station_name",
        "catchment_method",
        "poi_name",
        "retail_category",
        "amenity",
        "shop",
        "tourism",
        "office",
        "leisure",
        "geometry",
    ]
    for col in keep:
        if col not in combined.columns:
            combined[col] = ""
    return gpd.GeoDataFrame(combined[keep], geometry="geometry", crs=WGS84_CRS).drop_duplicates(
        subset=["station_id", "catchment_method", "poi_name", "geometry"]
    )


def summarize(pois: gpd.GeoDataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    total = (
        pois.groupby(["catchment_method", "station_id", "station_name"])
        .size()
        .reset_index(name="total_osm_pois")
    )
    categories = (
        pois.groupby(["catchment_method", "station_id", "station_name", "retail_category"])
        .size()
        .reset_index(name="poi_count")
    )
    pivot = categories.pivot_table(
        index=["catchment_method", "station_id", "station_name"],
        columns="retail_category",
        values="poi_count",
        fill_value=0,
    ).reset_index()
    return total, pivot


def main() -> None:
    ensure_directories()
    circular = gpd.read_file(BUFFERS_DIR / "mrt_station_500m_buffers.geojson").to_crs(WGS84_CRS)
    network = gpd.read_file(BUFFERS_DIR / "mrt_station_500m_walk_network_catchments.geojson").to_crs(WGS84_CRS)
    exits = gpd.read_file(BUFFERS_DIR / "mrt_exit_based_500m_buffers.geojson").to_crs(WGS84_CRS)

    all_pois = pd.concat(
        [
            collect_pois_for_catchments(circular, "circular_center_500m"),
            collect_pois_for_catchments(network, "walk_network_500m"),
            collect_pois_for_catchments(exits, "exit_union_500m"),
        ],
        ignore_index=True,
    )
    all_pois = gpd.GeoDataFrame(all_pois, geometry="geometry", crs=WGS84_CRS)
    all_pois.to_file(DATA_RAW / "osm_pois_by_catchment_method.geojson", driver="GeoJSON")
    all_pois.drop(columns="geometry").to_csv(TABLES_DIR / "osm_pois_by_catchment_method.csv", index=False)

    total, categories = summarize(all_pois)
    total.to_csv(TABLES_DIR / "catchment_method_total_poi_comparison.csv", index=False)
    categories.to_csv(TABLES_DIR / "catchment_method_category_comparison.csv", index=False)
    print("Saved catchment-method POI comparison tables.")


if __name__ == "__main__":
    main()
