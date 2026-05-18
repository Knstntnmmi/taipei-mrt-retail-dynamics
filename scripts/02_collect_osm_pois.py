import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

from project_config import (
    BUFFERS_DIR,
    DATA_RAW,
    OUTPUTS,
    TABLES_DIR,
    TAIWAN_METRIC_CRS,
    WGS84_CRS,
    ensure_directories,
)


OSM_TAGS = {
    "amenity": [
        "restaurant",
        "cafe",
        "fast_food",
        "bar",
        "pub",
        "food_court",
        "school",
        "college",
        "university",
        "clinic",
        "doctors",
        "dentist",
        "pharmacy",
        "bank",
        "atm",
        "post_office",
    ],
    "shop": True,
    "tourism": ["hotel", "hostel", "guest_house", "museum", "gallery"],
    "office": True,
    "leisure": ["fitness_centre", "sports_centre"],
}


def classify_poi(row: pd.Series) -> str:
    amenity = str(row.get("amenity", "")).lower()
    shop = str(row.get("shop", "")).lower()
    tourism = str(row.get("tourism", "")).lower()
    office = str(row.get("office", "")).lower()
    leisure = str(row.get("leisure", "")).lower()

    if amenity in {"restaurant", "fast_food", "food_court", "bar", "pub"}:
        return "food"
    if amenity == "cafe":
        return "cafe"
    if shop in {"convenience", "supermarket"}:
        return "convenience"
    if shop in {"clothes", "shoes", "fashion", "jewelry", "boutique", "bag"}:
        return "apparel/fashion"
    if shop in {"books", "stationery", "gift", "art", "furniture", "interior_decoration", "florist", "cosmetics"}:
        return "lifestyle/design"
    if amenity in {"school", "college", "university", "language_school", "music_school"}:
        return "education"
    if amenity in {"clinic", "doctors", "dentist", "pharmacy", "hospital"} or shop in {"chemist", "medical_supply", "optician"}:
        return "health"
    if amenity in {"bank", "atm", "post_office"} or office not in {"", "nan"} or shop in {"hairdresser", "laundry", "dry_cleaning", "copyshop", "travel_agency", "massage"} or leisure in {"fitness_centre", "sports_centre"}:
        return "services"
    if tourism in {"hotel", "hostel", "guest_house", "museum", "gallery"}:
        return "services"
    return "other"


def best_name(row: pd.Series) -> str:
    for column in ["name", "name:en", "name:zh", "brand"]:
        value = row.get(column)
        if pd.notna(value):
            return str(value)
    return ""


def collect_for_buffer(buffer_row: pd.Series) -> gpd.GeoDataFrame:
    import osmnx as ox

    polygon = buffer_row.geometry
    pois = ox.features_from_polygon(polygon, tags=OSM_TAGS)
    if pois.empty:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs=WGS84_CRS)

    pois = pois.reset_index()
    pois = pois[pois.geometry.notna()].copy()
    pois = pois[pois.geometry.geom_type.isin(["Point", "Polygon", "MultiPolygon"])].copy()
    pois["geometry"] = pois.geometry.representative_point()
    pois["station_id"] = buffer_row["station_id"]
    pois["station_name"] = buffer_row["station_name"]
    pois["poi_name"] = pois.apply(best_name, axis=1)
    pois["retail_category"] = pois.apply(classify_poi, axis=1)
    return pois


def write_empty_outputs(message: str) -> None:
    empty = pd.DataFrame(
        columns=[
            "station_id",
            "station_name",
            "poi_name",
            "retail_category",
            "amenity",
            "shop",
            "tourism",
            "office",
            "leisure",
            "geometry",
        ]
    )
    empty.to_csv(TABLES_DIR / "osm_pois_empty_reason.csv", index=False)
    (DATA_RAW / "osm_collection_status.json").write_text(json.dumps({"status": "failed", "message": message}, indent=2))
    print(message)


def main() -> None:
    ensure_directories()
    buffer_path = BUFFERS_DIR / "mrt_station_500m_buffers.geojson"
    if not buffer_path.exists():
        raise FileNotFoundError("Run scripts/01_create_buffers.py before collecting OSM POIs.")

    buffers = gpd.read_file(buffer_path).to_crs(WGS84_CRS)
    all_pois = []

    try:
        for _, row in buffers.iterrows():
            print(f"Collecting OSM POIs for {row['station_name']}...")
            pois = collect_for_buffer(row)
            all_pois.append(pois)
    except Exception as exc:
        write_empty_outputs(f"OSM POI collection failed: {exc}")
        return

    if not all_pois:
        write_empty_outputs("OSM POI collection returned no station results.")
        return

    combined = pd.concat(all_pois, ignore_index=True)
    if combined.empty:
        write_empty_outputs("OSM POI collection completed but returned zero POIs.")
        return

    pois = gpd.GeoDataFrame(combined, geometry="geometry", crs=WGS84_CRS)
    pois_metric = pois.to_crs(TAIWAN_METRIC_CRS)
    buffers_metric = buffers.to_crs(TAIWAN_METRIC_CRS)[["station_id", "geometry"]].rename(columns={"geometry": "buffer_geometry"})

    joined = gpd.sjoin(
        pois_metric,
        gpd.GeoDataFrame(buffers_metric, geometry="buffer_geometry", crs=TAIWAN_METRIC_CRS),
        how="inner",
        predicate="within",
    )
    joined = joined[joined["station_id_left"] == joined["station_id_right"]].copy()
    joined["station_id"] = joined["station_id_left"]
    joined = joined.drop(columns=[col for col in ["station_id_left", "station_id_right", "index_right"] if col in joined.columns])
    joined = joined.to_crs(WGS84_CRS)

    keep_columns = [
        "station_id",
        "station_name",
        "poi_name",
        "retail_category",
        "amenity",
        "shop",
        "tourism",
        "office",
        "leisure",
        "geometry",
    ]
    for col in keep_columns:
        if col not in joined.columns:
            joined[col] = ""
    joined = joined[keep_columns].drop_duplicates(subset=["station_id", "poi_name", "geometry"])

    joined.to_file(DATA_RAW / "osm_pois_within_500m.geojson", driver="GeoJSON")
    joined.drop(columns="geometry").to_csv(TABLES_DIR / "osm_pois_within_500m.csv", index=False)
    (DATA_RAW / "osm_collection_status.json").write_text(
        json.dumps({"status": "success", "poi_count": int(len(joined))}, indent=2)
    )
    print(f"Saved {len(joined)} OSM POIs within station buffers.")


if __name__ == "__main__":
    main()
