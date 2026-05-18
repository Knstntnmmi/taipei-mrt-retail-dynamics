import geopandas as gpd

from project_config import DATA_RAW, TABLES_DIR, ensure_directories


def main() -> None:
    ensure_directories()
    poi_path = DATA_RAW / "osm_pois_within_500m.geojson"
    if not poi_path.exists():
        raise FileNotFoundError("Run scripts/02_collect_osm_pois.py first.")

    pois = gpd.read_file(poi_path)
    sample = (
        pois.sort_values(["station_id", "retail_category", "poi_name"])
        .groupby(["station_id", "retail_category"], group_keys=False)
        .head(3)
        .copy()
    )
    sample["manual_category_check"] = ""
    sample["manual_notes"] = ""
    keep = [
        "station_id",
        "station_name",
        "poi_name",
        "retail_category",
        "amenity",
        "shop",
        "tourism",
        "office",
        "leisure",
        "manual_category_check",
        "manual_notes",
    ]
    sample[keep].to_csv(TABLES_DIR / "manual_osm_category_validation_sample.csv", index=False)
    print(f"Saved manual validation sample with {len(sample)} rows.")


if __name__ == "__main__":
    main()
