import geopandas as gpd
import pandas as pd

from project_config import (
    BUFFER_METERS,
    BUFFERS_DIR,
    DATA_PROCESSED,
    STATIONS,
    TAIWAN_METRIC_CRS,
    WGS84_CRS,
    ensure_directories,
)


def create_station_points() -> gpd.GeoDataFrame:
    station_df = pd.DataFrame(STATIONS)
    stations = gpd.GeoDataFrame(
        station_df,
        geometry=gpd.points_from_xy(station_df["lon"], station_df["lat"]),
        crs=WGS84_CRS,
    )
    return stations


def create_buffers(stations: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    stations_metric = stations.to_crs(TAIWAN_METRIC_CRS)
    buffers_metric = stations_metric.copy()
    buffers_metric["buffer_m"] = BUFFER_METERS
    buffers_metric["geometry"] = stations_metric.geometry.buffer(BUFFER_METERS)
    return buffers_metric.to_crs(WGS84_CRS)


def main() -> None:
    ensure_directories()
    stations = create_station_points()
    buffers = create_buffers(stations)

    stations.to_file(DATA_PROCESSED / "mrt_station_points.geojson", driver="GeoJSON")
    buffers.to_file(BUFFERS_DIR / "mrt_station_500m_buffers.geojson", driver="GeoJSON")

    for _, row in buffers.iterrows():
        single = buffers[buffers["station_id"] == row["station_id"]]
        single.to_file(BUFFERS_DIR / f"{row['station_id']}_500m_buffer.geojson", driver="GeoJSON")

    print("Created station points and 500 m buffers.")
    print(f"Combined buffers: {BUFFERS_DIR / 'mrt_station_500m_buffers.geojson'}")


if __name__ == "__main__":
    main()
