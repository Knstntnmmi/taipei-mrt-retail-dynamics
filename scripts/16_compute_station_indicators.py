from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"


def compute_indicators() -> pd.DataFrame:
    events = pd.read_csv(TABLES_DIR / "station_business_open_close_latest_month_summary.csv")
    pois = pd.read_csv(TABLES_DIR / "total_poi_count_by_station.csv")
    flow = pd.read_csv(TABLES_DIR / "mrt_passenger_flow_by_station.csv")

    indicators = events.merge(pois[["station_id", "total_osm_pois"]], on="station_id")
    indicators = indicators.merge(flow[["station_id", "total_station_flow"]], on="station_id")

    indicators["turnover_events_per_100_pois"] = (
        indicators["total_events"] / indicators["total_osm_pois"] * 100
    ).round(2)
    indicators["openings_per_100_pois"] = (
        indicators["openings"] / indicators["total_osm_pois"] * 100
    ).round(2)
    indicators["closures_per_100_pois"] = (
        indicators["closures"] / indicators["total_osm_pois"] * 100
    ).round(2)
    indicators["passenger_flow_per_poi"] = (
        indicators["total_station_flow"] / indicators["total_osm_pois"]
    ).round(1)
    indicators["event_share_pct"] = (
        indicators["total_events"] / indicators["total_events"].sum() * 100
    ).round(2)
    indicators["poi_share_pct"] = (
        indicators["total_osm_pois"] / indicators["total_osm_pois"].sum() * 100
    ).round(2)
    indicators["flow_share_pct"] = (
        indicators["total_station_flow"] / indicators["total_station_flow"].sum() * 100
    ).round(2)

    columns = [
        "station_id",
        "station_name",
        "event_month",
        "openings",
        "closures",
        "net_change",
        "total_events",
        "closure_rate_of_events_pct",
        "total_osm_pois",
        "total_station_flow",
        "turnover_events_per_100_pois",
        "openings_per_100_pois",
        "closures_per_100_pois",
        "passenger_flow_per_poi",
        "event_share_pct",
        "poi_share_pct",
        "flow_share_pct",
    ]
    return indicators[columns].sort_values("turnover_events_per_100_pois", ascending=False)


def make_chart(indicators: pd.DataFrame) -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    plot_data = indicators.sort_values("turnover_events_per_100_pois")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.barh(
        plot_data["station_name"],
        plot_data["turnover_events_per_100_pois"],
        color=["#557A95", "#76B900", "#2F7D88"],
    )
    ax.set_title("Latest Business Turnover Normalized by Mapped Retail Base", weight="bold")
    ax.set_xlabel("Opening + closure events per 100 mapped places")
    ax.grid(axis="x", color="#D9E2DF", linewidth=0.8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for y, value in enumerate(plot_data["turnover_events_per_100_pois"]):
        ax.text(value + 0.08, y, f"{value:.2f}", va="center", fontsize=10)
    ax.set_xlim(0, max(plot_data["turnover_events_per_100_pois"]) * 1.18)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "station_turnover_per_100_pois.png", dpi=180)
    plt.close(fig)


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    indicators = compute_indicators()
    indicators.to_csv(TABLES_DIR / "station_normalized_turnover_indicators.csv", index=False)
    make_chart(indicators)
    print(indicators.to_string(index=False))


if __name__ == "__main__":
    main()
