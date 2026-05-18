import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from project_config import BUFFERS_DIR, CHARTS_DIR, DATA_RAW, MAPS_DIR, TABLES_DIR, ensure_directories


CATEGORY_COLORS = {
    "food": "#d95f02",
    "cafe": "#8c6d31",
    "convenience": "#1b9e77",
    "apparel/fashion": "#7570b3",
    "lifestyle/design": "#e7298a",
    "education": "#66a61e",
    "health": "#e6ab02",
    "services": "#1f78b4",
    "other": "#7f7f7f",
}


def save_total_bar(total_counts: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(total_counts["station_name"], total_counts["total_osm_pois"], color="#2f6f8f")
    ax.set_title("Total OSM Retail and Commercial POIs within 500 m")
    ax.set_ylabel("POI count")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "total_poi_count_by_station.png", dpi=200)
    plt.close(fig)


def save_stacked_chart(table: pd.DataFrame, output_name: str, ylabel: str, title: str) -> None:
    plot_df = table.set_index("station_name").drop(columns=["station_id"], errors="ignore")
    colors = [CATEGORY_COLORS.get(col, "#999999") for col in plot_df.columns]
    ax = plot_df.plot(kind="bar", stacked=True, figsize=(9, 5.5), color=colors)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=15)
    ax.legend(title="Category", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / output_name, dpi=200)
    plt.close(fig)


def save_buffer_maps() -> None:
    buffers = gpd.read_file(BUFFERS_DIR / "mrt_station_500m_buffers.geojson")
    fig, ax = plt.subplots(figsize=(7, 7))
    buffers.boundary.plot(ax=ax, linewidth=2, color="#2f6f8f")
    buffers.representative_point().plot(ax=ax, color="#d95f02", markersize=35)
    for _, row in buffers.iterrows():
        point = row.geometry.representative_point()
        ax.annotate(row["station_name"], (point.x, point.y), xytext=(4, 4), textcoords="offset points")
    ax.set_title("500 m MRT Station Catchments")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(MAPS_DIR / "combined_station_buffers.png", dpi=200)
    plt.close(fig)

    for _, row in buffers.iterrows():
        single = buffers[buffers["station_id"] == row["station_id"]]
        fig, ax = plt.subplots(figsize=(6, 6))
        single.boundary.plot(ax=ax, linewidth=2, color="#2f6f8f")
        single.representative_point().plot(ax=ax, color="#d95f02", markersize=35)
        ax.set_title(f"{row['station_name']} 500 m Catchment")
        ax.set_axis_off()
        fig.tight_layout()
        fig.savefig(MAPS_DIR / f"{row['station_id']}_buffer_map.png", dpi=200)
        plt.close(fig)

    network_path = BUFFERS_DIR / "mrt_station_500m_walk_network_catchments.geojson"
    exit_path = BUFFERS_DIR / "mrt_exit_based_500m_buffers.geojson"
    if network_path.exists() and exit_path.exists():
        network = gpd.read_file(network_path).to_crs(buffers.crs)
        exits = gpd.read_file(exit_path).to_crs(buffers.crs)
        fig, ax = plt.subplots(figsize=(8, 8))
        buffers.boundary.plot(ax=ax, linewidth=2, color="#2f6f8f", label="Circular center buffer")
        network.boundary.plot(ax=ax, linewidth=2, color="#d95f02", label="Walk-network catchment")
        exits.boundary.plot(ax=ax, linewidth=2, color="#1b9e77", label="Exit-union buffer")
        ax.set_title("Catchment Method Comparison")
        ax.set_axis_off()
        ax.legend(loc="best")
        fig.tight_layout()
        fig.savefig(MAPS_DIR / "catchment_method_comparison_map.png", dpi=200)
        plt.close(fig)


def save_poi_maps() -> None:
    poi_path = DATA_RAW / "osm_pois_within_500m.geojson"
    if not poi_path.exists():
        return
    pois = gpd.read_file(poi_path)
    if pois.empty:
        return
    buffers = gpd.read_file(BUFFERS_DIR / "mrt_station_500m_buffers.geojson")

    fig, ax = plt.subplots(figsize=(8, 8))
    buffers.boundary.plot(ax=ax, linewidth=2, color="#333333")
    for category, color in CATEGORY_COLORS.items():
        subset = pois[pois["retail_category"] == category]
        if not subset.empty:
            subset.plot(ax=ax, markersize=12, color=color, label=category, alpha=0.75)
    ax.set_title("OSM POIs within 500 m MRT Catchments")
    ax.set_axis_off()
    ax.legend(title="Category", bbox_to_anchor=(1.02, 1), loc="upper left", markerscale=1.5)
    fig.tight_layout()
    fig.savefig(MAPS_DIR / "combined_poi_map.png", dpi=200)
    plt.close(fig)

    for station_id, station_pois in pois.groupby("station_id"):
        station_buffer = buffers[buffers["station_id"] == station_id]
        station_name = station_pois["station_name"].iloc[0]
        fig, ax = plt.subplots(figsize=(6, 6))
        station_buffer.boundary.plot(ax=ax, linewidth=2, color="#333333")
        for category, color in CATEGORY_COLORS.items():
            subset = station_pois[station_pois["retail_category"] == category]
            if not subset.empty:
                subset.plot(ax=ax, markersize=14, color=color, label=category, alpha=0.75)
        ax.set_title(f"{station_name} OSM POIs")
        ax.set_axis_off()
        ax.legend(title="Category", fontsize=8, loc="best")
        fig.tight_layout()
        fig.savefig(MAPS_DIR / f"{station_id}_poi_map.png", dpi=200)
        plt.close(fig)


def save_extension_charts() -> None:
    flow_path = TABLES_DIR / "mrt_passenger_flow_by_station.csv"
    if flow_path.exists():
        flow = pd.read_csv(flow_path)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(flow["station_name"], flow["total_station_flow"], color="#4c78a8")
        ax.set_title("Verified MRT Passenger Flow by Station")
        ax.set_ylabel("Entries + exits")
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=15)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "mrt_passenger_flow_by_station.png", dpi=200)
        plt.close(fig)

    catchment_path = TABLES_DIR / "catchment_method_total_poi_comparison.csv"
    if catchment_path.exists():
        catchment = pd.read_csv(catchment_path)
        pivot = catchment.pivot(index="station_name", columns="catchment_method", values="total_osm_pois")
        ax = pivot.plot(kind="bar", figsize=(9, 5), color=["#2f6f8f", "#1b9e77", "#d95f02"])
        ax.set_title("POI Count Sensitivity by Catchment Method")
        ax.set_ylabel("OSM POI count")
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=15)
        ax.legend(title="Catchment method", bbox_to_anchor=(1.02, 1), loc="upper left")
        fig = ax.get_figure()
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "catchment_method_total_poi_comparison.png", dpi=200)
        plt.close(fig)


def main() -> None:
    ensure_directories()
    total_counts = pd.read_csv(TABLES_DIR / "total_poi_count_by_station.csv")
    category_counts = pd.read_csv(TABLES_DIR / "retail_category_count_by_station.csv")
    category_shares = pd.read_csv(TABLES_DIR / "retail_category_share_by_station.csv")

    save_total_bar(total_counts)
    save_stacked_chart(
        category_counts,
        "retail_category_count_by_station.png",
        "POI count",
        "Retail Category Counts by MRT Station Catchment",
    )
    save_stacked_chart(
        category_shares,
        "retail_category_share_by_station.png",
        "Share of station POIs",
        "Retail Category Shares by MRT Station Catchment",
    )
    save_buffer_maps()
    save_poi_maps()
    save_extension_charts()
    print("Saved charts and maps.")


if __name__ == "__main__":
    main()
