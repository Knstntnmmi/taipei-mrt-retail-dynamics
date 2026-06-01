import io
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"
BUFFERS_PATH = PROJECT_ROOT / "outputs" / "buffers" / "mrt_station_500m_buffers.geojson"

TAIPEI_BUSINESS_EVENTS = {
    "opening": {
        "url": "https://data.taipei/api/frontstage/tpeod/dataset/resource.download?rid=a1cab84c-2213-4d22-b7dd-96f62630ad08",
        "raw_name": "taipei_business_establishments_latest_month_raw.csv",
        "date_column": "設立日期",
    },
    "closure": {
        "url": "https://data.taipei/api/frontstage/tpeod/dataset/resource.download?rid=4fe767dc-79fb-48ca-8e4d-6b4f05e9f4a3",
        "raw_name": "taipei_business_closures_latest_month_raw.csv",
        "date_column": "歇業日期",
    },
}


def ensure_dirs() -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def roc_date_to_iso(value: object) -> str:
    text = str(value).strip().replace(".0", "")
    if len(text) < 7:
        return ""
    year = int(text[:3]) + 1911
    month = int(text[3:5])
    day = int(text[5:7])
    return f"{year:04d}-{month:02d}-{day:02d}"


def download_event_file(event_type: str, config: dict[str, str]) -> pd.DataFrame:
    response = requests.get(config["url"], timeout=45)
    response.raise_for_status()
    raw_path = DATA_RAW / config["raw_name"]
    raw_path.write_bytes(response.content)

    df = pd.read_csv(io.BytesIO(response.content), encoding="utf-8-sig")
    df = df.rename(
        columns={
            "統一編號": "business_id",
            "商業名稱": "business_name",
            "商業地址": "business_address",
            config["date_column"]: "event_date_roc",
            "Longitude": "lon",
            "Latitude": "lat",
        }
    )
    df["event_type"] = event_type
    df["event_date"] = df["event_date_roc"].apply(roc_date_to_iso)
    df["event_month"] = df["event_date"].str.slice(0, 7)
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    return df[["event_type", "event_date", "event_month", "business_id", "business_name", "business_address", "lon", "lat"]]


def collect_latest_events() -> pd.DataFrame:
    frames = [download_event_file(event_type, config) for event_type, config in TAIPEI_BUSINESS_EVENTS.items()]
    events = pd.concat(frames, ignore_index=True)
    events = events.dropna(subset=["lon", "lat"])
    events = events[(events["lon"].between(121.3, 121.8)) & (events["lat"].between(24.8, 25.3))]
    return events


def spatial_join_to_station_buffers(events: pd.DataFrame) -> gpd.GeoDataFrame:
    buffers = gpd.read_file(BUFFERS_PATH)[["station_id", "station_name", "geometry"]]
    points = gpd.GeoDataFrame(
        events,
        geometry=gpd.points_from_xy(events["lon"], events["lat"]),
        crs="EPSG:4326",
    )
    return gpd.sjoin(points, buffers, predicate="within", how="inner").drop(columns=["index_right"])


def summarize_station_events(joined: pd.DataFrame) -> pd.DataFrame:
    if joined.empty:
        buffers = gpd.read_file(BUFFERS_PATH)[["station_id", "station_name"]]
        summary = buffers.copy()
        summary["event_month"] = ""
        summary["openings"] = 0
        summary["closures"] = 0
    else:
        summary = (
            joined.pivot_table(
                index=["station_id", "station_name", "event_month"],
                columns="event_type",
                values="business_id",
                aggfunc="count",
                fill_value=0,
            )
            .reset_index()
            .rename_axis(None, axis=1)
        )
        for col in ["opening", "closure"]:
            if col not in summary.columns:
                summary[col] = 0
        summary = summary.rename(columns={"opening": "openings", "closure": "closures"})

    summary["net_change"] = summary["openings"] - summary["closures"]
    summary["total_events"] = summary["openings"] + summary["closures"]
    summary["closure_rate_of_events_pct"] = (
        summary["closures"] / summary["total_events"].replace(0, pd.NA) * 100
    ).fillna(0).round(2)
    return summary.sort_values(["station_name", "event_month"])


def save_chart(summary: pd.DataFrame) -> None:
    station_order = ["Gongguan", "Zhongxiao Fuxing", "Zhongshan"]
    plot_df = summary.copy()
    plot_df["station_name"] = pd.Categorical(plot_df["station_name"], station_order, ordered=True)
    plot_df = plot_df.sort_values("station_name")
    plot_df["label"] = plot_df["station_name"]
    fig, ax = plt.subplots(figsize=(9.5, 5))
    x = range(len(plot_df))
    ax.bar([i - 0.18 for i in x], plot_df["openings"], width=0.36, label="Openings", color="#2E9D68")
    ax.bar([i + 0.18 for i in x], plot_df["closures"], width=0.36, label="Closures", color="#D86135")
    for i, row in enumerate(plot_df.itertuples()):
        ax.text(i - 0.18, row.openings + 0.25, str(int(row.openings)), ha="center", va="bottom", fontsize=10)
        ax.text(i + 0.18, row.closures + 0.25, str(int(row.closures)), ha="center", va="bottom", fontsize=10)
    ax.axhline(0, color="#1B2A2F", linewidth=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(plot_df["label"])
    ax.set_ylabel("Businesses")
    month = ", ".join(sorted(str(m) for m in plot_df["event_month"].dropna().unique() if str(m)))
    ax.set_title(f"Station-Level Business Openings and Closures, {month or 'latest available month'}")
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#DDE7E4", linewidth=0.8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "station_business_open_close_latest_month.png", dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    events = collect_latest_events()
    joined = spatial_join_to_station_buffers(events)
    summary = summarize_station_events(joined)

    events.to_csv(TABLES_DIR / "taipei_business_events_latest_month_all_city.csv", index=False)
    joined.drop(columns="geometry").to_csv(TABLES_DIR / "station_business_events_latest_month.csv", index=False)
    summary.to_csv(TABLES_DIR / "station_business_open_close_latest_month_summary.csv", index=False)
    status = pd.DataFrame(
        [
            {
                "metric": "station_level_geocoded_business_events",
                "value": ", ".join(sorted(summary["event_month"].dropna().astype(str).unique())),
                "status": "verified station-level latest monthly data",
            },
            {
                "metric": "station_level_2022_present_history",
                "value": "not available from the current Taipei City geocoded monthly resources",
                "status": "missing archive or historical geocoded panel",
            },
            {
                "metric": "source",
                "value": "Taipei City geocoded business establishment and closure records",
                "status": "official source",
            },
        ]
    )
    status.to_csv(TABLES_DIR / "station_business_open_close_data_status.csv", index=False)
    save_chart(summary)

    print(summary.to_string(index=False))
    print("\nNote: this is station-level only for the currently published Taipei monthly geocoded business event files.")


if __name__ == "__main__":
    main()
