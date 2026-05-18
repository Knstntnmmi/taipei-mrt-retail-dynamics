import geopandas as gpd
import pandas as pd

from project_config import DATA_RAW, TABLES_DIR, ensure_directories


CATEGORIES = [
    "food",
    "cafe",
    "convenience",
    "apparel/fashion",
    "lifestyle/design",
    "education",
    "health",
    "services",
    "other",
]


def main() -> None:
    ensure_directories()
    poi_path = DATA_RAW / "osm_pois_within_500m.geojson"
    if not poi_path.exists():
        raise FileNotFoundError("Run scripts/02_collect_osm_pois.py before analyzing retail mix.")

    pois = gpd.read_file(poi_path)
    if pois.empty:
        raise ValueError("The OSM POI file exists but contains no records.")

    total_counts = (
        pois.groupby(["station_id", "station_name"])
        .size()
        .reset_index(name="total_osm_pois")
        .sort_values("total_osm_pois", ascending=False)
    )

    category_counts = (
        pois.groupby(["station_id", "station_name", "retail_category"])
        .size()
        .reset_index(name="poi_count")
    )
    category_pivot = (
        category_counts.pivot_table(
            index=["station_id", "station_name"],
            columns="retail_category",
            values="poi_count",
            fill_value=0,
        )
        .reindex(columns=CATEGORIES, fill_value=0)
        .reset_index()
    )
    category_pivot[CATEGORIES] = category_pivot[CATEGORIES].astype(int)

    share_pivot = category_pivot.copy()
    numeric_cols = [col for col in CATEGORIES if col in share_pivot.columns]
    totals = share_pivot[numeric_cols].sum(axis=1).replace(0, pd.NA)
    share_pivot[numeric_cols] = share_pivot[numeric_cols].div(totals, axis=0).fillna(0).round(4)

    total_counts.to_csv(TABLES_DIR / "total_poi_count_by_station.csv", index=False)
    category_pivot.to_csv(TABLES_DIR / "retail_category_count_by_station.csv", index=False)
    share_pivot.to_csv(TABLES_DIR / "retail_category_share_by_station.csv", index=False)

    print("Saved comparison tables.")


if __name__ == "__main__":
    main()
