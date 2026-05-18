from pathlib import Path

import geopandas as gpd
import pandas as pd

from project_config import (
    BUFFERS_DIR,
    DATA_PROCESSED,
    STATION_NAME_ZH,
    TABLES_DIR,
    TAIWAN_METRIC_CRS,
    WGS84_CRS,
    ensure_directories,
)


SOURCE_EXITS = Path("/Users/konstantin/Documents/Playground/retail_vacancy_prediction/data/processed/mrt_exits_utf8.csv")


def station_id_from_exit_name(name: str):
    for station_id, zh_name in STATION_NAME_ZH.items():
        if str(name).startswith(f"{zh_name}站"):
            return station_id
    return None


def main() -> None:
    ensure_directories()
    if not SOURCE_EXITS.exists():
        raise FileNotFoundError(f"Missing source station-exit file: {SOURCE_EXITS}")

    exits = pd.read_csv(SOURCE_EXITS)
    exits["station_id"] = exits["出入口名稱"].apply(station_id_from_exit_name)
    exits = exits[exits["station_id"].notna()].copy()
    exits = exits.rename(
        columns={
            "出入口名稱": "exit_name_zh",
            "出入口編號": "exit_number",
            "經度": "lon",
            "緯度": "lat",
            "是否為無障礙用": "accessible_zh",
        }
    )
    exits["station_name"] = exits["station_id"].map(
        {
            "gongguan": "Gongguan",
            "zhongxiao_fuxing": "Zhongxiao Fuxing",
            "zhongshan": "Zhongshan",
        }
    )
    exits_gdf = gpd.GeoDataFrame(
        exits[["station_id", "station_name", "exit_name_zh", "exit_number", "lon", "lat", "accessible_zh"]],
        geometry=gpd.points_from_xy(exits["lon"], exits["lat"]),
        crs=WGS84_CRS,
    )
    exits_gdf.to_file(DATA_PROCESSED / "mrt_station_exits.geojson", driver="GeoJSON")
    exits_gdf.drop(columns="geometry").to_csv(TABLES_DIR / "mrt_station_exits.csv", index=False)

    exits_metric = exits_gdf.to_crs(TAIWAN_METRIC_CRS)
    exit_buffers = exits_metric.dissolve(by=["station_id", "station_name"]).reset_index()
    exit_buffers["geometry"] = exit_buffers.geometry.buffer(500)
    exit_buffers = exit_buffers.to_crs(WGS84_CRS)
    exit_buffers.to_file(BUFFERS_DIR / "mrt_exit_based_500m_buffers.geojson", driver="GeoJSON")

    counts = exits_gdf.groupby(["station_id", "station_name"]).size().reset_index(name="exit_count")
    counts.to_csv(TABLES_DIR / "mrt_exit_count_by_station.csv", index=False)
    print(f"Saved {len(exits_gdf)} station exits and exit-based buffers.")


if __name__ == "__main__":
    main()
