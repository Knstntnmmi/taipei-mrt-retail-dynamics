from pathlib import Path
import textwrap

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"
MAPS_DIR = PROJECT_ROOT / "outputs" / "poster" / "station_profile_maps"


STATION_ORDER = ["gongguan", "zhongxiao_fuxing", "zhongshan"]
STATION_FRAMING = {
    "gongguan": {
        "title": "Gongguan",
        "subtitle": "Student food node",
        "note": "Dense food, cafe, health, and everyday-service activity around a university-oriented station area.",
        "short_note": "University-oriented food and everyday-service catchment.",
        "map": MAPS_DIR / "gongguan_poster_map.png",
        "color": "#76B900",
    },
    "zhongxiao_fuxing": {
        "title": "Zhongxiao Fuxing",
        "subtitle": "Transfer and premium retail node",
        "note": "High passenger flow, but simple point counts understate vertical malls, department stores, and underground retail.",
        "short_note": "Vertical malls may be undercounted.",
        "map": MAPS_DIR / "zhongxiao_fuxing_poster_map.png",
        "color": "#A3FF12",
    },
    "zhongshan": {
        "title": "Zhongshan",
        "subtitle": "Shopping, culture, and tourism node",
        "note": "Largest observed point-of-interest count and highest verified passenger flow among the three stations.",
        "short_note": "Highest latest-month turnover and mapped retail volume.",
        "map": MAPS_DIR / "zhongshan_poster_map.png",
        "color": "#5EC64D",
    },
}

CATEGORY_LABELS = {
    "food": "Food",
    "cafe": "Cafe",
    "convenience": "Convenience",
    "apparel/fashion": "Apparel / fashion",
    "lifestyle/design": "Lifestyle / design",
    "education": "Education",
    "health": "Health",
    "services": "Services",
    "other": "Other",
}
CATEGORY_SHORT_LABELS = {
    **CATEGORY_LABELS,
    "apparel/fashion": "Fashion",
    "lifestyle/design": "Design",
}
CATEGORY_COLORS = {
    "food": "#76B900",
    "cafe": "#A3FF12",
    "convenience": "#35D07F",
    "apparel/fashion": "#C7F464",
    "lifestyle/design": "#86C232",
    "education": "#D7FF66",
    "health": "#52B788",
    "services": "#4D908E",
    "other": "#8FA198",
}

TEXT = "#F1F7F0"
MUTED = "#AAB8AE"
BG = "#050806"
CARD = "#111713"
CARD_ALT = "#172119"
GREEN = "#76B900"
RED = "#F05A28"
LINE = "#2D3A31"


def load_inputs() -> pd.DataFrame:
    categories = pd.read_csv(TABLES_DIR / "retail_category_count_by_station.csv")
    totals = pd.read_csv(TABLES_DIR / "total_poi_count_by_station.csv")
    flow = pd.read_csv(TABLES_DIR / "mrt_passenger_flow_by_station.csv")
    events = pd.read_csv(TABLES_DIR / "station_business_open_close_latest_month_summary.csv")

    categories = categories.merge(totals[["station_id", "total_osm_pois"]], on="station_id")
    categories = categories.merge(flow[["station_id", "total_station_flow"]], on="station_id")
    categories = categories.merge(
        events[
            [
                "station_id",
                "event_month",
                "openings",
                "closures",
                "net_change",
                "total_events",
                "closure_rate_of_events_pct",
            ]
        ],
        on="station_id",
        how="left",
    )
    categories[["openings", "closures", "net_change", "total_events"]] = categories[
        ["openings", "closures", "net_change", "total_events"]
    ].fillna(0).astype(int)
    categories["closure_rate_of_events_pct"] = categories["closure_rate_of_events_pct"].fillna(0)
    categories["event_month"] = categories["event_month"].fillna("latest month")

    indicator_path = TABLES_DIR / "station_normalized_turnover_indicators.csv"
    if indicator_path.exists():
        indicators = pd.read_csv(indicator_path)
        indicator_cols = [
            "station_id",
            "turnover_events_per_100_pois",
            "openings_per_100_pois",
            "closures_per_100_pois",
            "passenger_flow_per_poi",
            "event_share_pct",
        ]
        categories = categories.merge(indicators[indicator_cols], on="station_id", how="left")
    else:
        categories["turnover_events_per_100_pois"] = (
            categories["total_events"] / categories["total_osm_pois"] * 100
        ).round(2)
        categories["passenger_flow_per_poi"] = (
            categories["total_station_flow"] / categories["total_osm_pois"]
        ).round(1)
        categories["event_share_pct"] = (
            categories["total_events"] / categories["total_events"].sum() * 100
        ).round(2)
    return categories


def rounded_panel(ax, radius: float = 0.035) -> None:
    ax.axis("off")
    ax.add_patch(
        FancyBboxPatch(
            (0, 0),
            1,
            1,
            boxstyle=f"round,pad=0.012,rounding_size={radius}",
            linewidth=1,
            edgecolor=LINE,
            facecolor=CARD,
            transform=ax.transAxes,
            clip_on=False,
        )
    )


def add_wrapped_text(ax, x: float, y: float, text: str, width: int, **kwargs) -> None:
    kwargs.setdefault("va", "top")
    ax.text(x, y, "\n".join(textwrap.wrap(text, width=width)), transform=ax.transAxes, **kwargs)


def draw_metric_pill(ax, x: float, y: float, label: str, value: str, color: str) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            0.25,
            0.16,
            boxstyle="round,pad=0.01,rounding_size=0.028",
            linewidth=0,
            facecolor=color,
            transform=ax.transAxes,
        )
    )
    ax.text(
        x + 0.025,
        y + 0.095,
        value,
        transform=ax.transAxes,
        fontsize=18,
        weight="bold",
        color="white",
    )
    ax.text(x + 0.025, y + 0.035, label, transform=ax.transAxes, fontsize=9.5, color="white")


def draw_turnover_panel(ax, station: pd.Series, color: str) -> None:
    rounded_panel(ax)
    month = station["event_month"]
    openings = int(station["openings"])
    closures = int(station["closures"])
    total_events = int(station["total_events"])
    net_change = int(station["net_change"])
    closure_rate = float(station["closure_rate_of_events_pct"])
    max_events = max(openings, closures, 1)

    ax.text(
        0.055,
        0.88,
        "Business turnover inside 500 m",
        transform=ax.transAxes,
        fontsize=16,
        weight="bold",
        color=TEXT,
    )
    ax.text(
        0.055,
        0.805,
        f"Official Taipei City geocoded records, {month}",
        transform=ax.transAxes,
        fontsize=10.5,
        color=MUTED,
    )

    draw_metric_pill(ax, 0.055, 0.59, "openings", f"+{openings}", GREEN)
    draw_metric_pill(ax, 0.34, 0.59, "closures", f"-{closures}", RED)
    draw_metric_pill(ax, 0.625, 0.59, "net change", f"{net_change:+d}", color)

    ax.text(
        0.055,
        0.43,
        "Opening and closure volume",
        transform=ax.transAxes,
        fontsize=11.5,
        weight="bold",
        color=TEXT,
    )
    ax.text(0.055, 0.34, "Open", transform=ax.transAxes, fontsize=10.5, color=MUTED)
    ax.add_patch(FancyBboxPatch((0.19, 0.347), 0.67, 0.052, boxstyle="round,pad=0,rounding_size=0.014", linewidth=0, facecolor="#243024", transform=ax.transAxes))
    ax.add_patch(FancyBboxPatch((0.19, 0.347), 0.67 * openings / max_events, 0.052, boxstyle="round,pad=0,rounding_size=0.014", linewidth=0, facecolor=GREEN, transform=ax.transAxes))
    ax.text(0.89, 0.34, f"{openings}", transform=ax.transAxes, fontsize=11, weight="bold", color=TEXT)

    ax.text(0.055, 0.25, "Close", transform=ax.transAxes, fontsize=10.5, color=MUTED)
    ax.add_patch(FancyBboxPatch((0.19, 0.257), 0.67, 0.052, boxstyle="round,pad=0,rounding_size=0.014", linewidth=0, facecolor="#3A211C", transform=ax.transAxes))
    ax.add_patch(FancyBboxPatch((0.19, 0.257), 0.67 * closures / max_events, 0.052, boxstyle="round,pad=0,rounding_size=0.014", linewidth=0, facecolor=RED, transform=ax.transAxes))
    ax.text(0.89, 0.25, f"{closures}", transform=ax.transAxes, fontsize=11, weight="bold", color=TEXT)

    ax.text(0.055, 0.115, f"{closure_rate:.2f}% closure rate ({total_events} latest-month events)", transform=ax.transAxes, fontsize=11.5, weight="bold", color=TEXT)
    ax.text(0.055, 0.055, "Verified station-level evidence; not a full 2022-present station history.", transform=ax.transAxes, fontsize=10, color=MUTED)


def draw_station_comparison(ax, categories: pd.DataFrame, station_id: str) -> None:
    ax.axis("off")
    rounded_panel(ax)
    ax.text(0.055, 0.91, "Three-station turnover ranking", transform=ax.transAxes, fontsize=15, weight="bold", color=TEXT)
    ax.text(0.055, 0.845, "Bar length = total openings + closures (latest month)", transform=ax.transAxes, fontsize=9.2, color=MUTED)
    max_events = max(categories["total_events"].max(), 1)
    labels = {
        "gongguan": "Gongguan",
        "zhongxiao_fuxing": "Zhongxiao Fuxing",
        "zhongshan": "Zhongshan",
    }
    for index, compare_id in enumerate(STATION_ORDER):
        row = categories[categories["station_id"] == compare_id].iloc[0]
        y = 0.68 - index * 0.24
        active = compare_id == station_id
        color = STATION_FRAMING[compare_id]["color"] if active else "#53635A"
        text_color = TEXT if active else MUTED
        ax.text(0.055, y + 0.11, labels[compare_id], transform=ax.transAxes, fontsize=11.5, weight="bold", color=text_color)
        ax.text(0.055, y + 0.035, f"+{int(row['openings'])} open / -{int(row['closures'])} close", transform=ax.transAxes, fontsize=10.5, color=text_color)
        ax.add_patch(
            FancyBboxPatch(
                (0.43, y + 0.06),
                0.48,
                0.055,
                boxstyle="round,pad=0,rounding_size=0.01",
                linewidth=0,
                facecolor="#263229",
                transform=ax.transAxes,
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (0.43, y + 0.06),
                0.48 * row["total_events"] / max_events,
                0.055,
                boxstyle="round,pad=0,rounding_size=0.01",
                linewidth=0,
                facecolor=color,
                transform=ax.transAxes,
            )
        )
        ax.text(
            0.915,
            y + 0.0875,
            f"{int(row['total_events'])}",
            transform=ax.transAxes,
            fontsize=10,
            weight="bold",
            ha="left",
            va="center",
            color=text_color,
        )
        ax.text(
            0.055,
            y - 0.04,
            f"{int(row['total_osm_pois']):,} mapped places  ·  {int(row['total_station_flow']):,} flow",
            transform=ax.transAxes,
            fontsize=9.1,
            color=MUTED,
        )


def draw_normalized_metrics(ax, categories: pd.DataFrame, station_id: str) -> None:
    rounded_panel(ax)
    station = categories[categories["station_id"] == station_id].iloc[0]
    max_turnover = max(categories["turnover_events_per_100_pois"].max(), 1)
    max_flow_per_poi = max(categories["passenger_flow_per_poi"].max(), 1)
    color = STATION_FRAMING[station_id]["color"]

    ax.text(0.055, 0.82, "Normalized indicators", transform=ax.transAxes, fontsize=14.5, weight="bold", color=TEXT)
    ax.text(0.055, 0.7, "Derived rates make station areas comparable.", transform=ax.transAxes, fontsize=9.8, color=MUTED)

    metrics = [
        (
            "Turnover",
            "events / 100 mapped places",
            f"{station['turnover_events_per_100_pois']:.2f}",
            station["turnover_events_per_100_pois"] / max_turnover,
        ),
        (
            "Flow intensity",
            "passengers / mapped place",
            f"{station['passenger_flow_per_poi']:.1f}",
            station["passenger_flow_per_poi"] / max_flow_per_poi,
        ),
        (
            "Event share",
            "of three-station total",
            f"{station['event_share_pct']:.1f}%",
            station["event_share_pct"] / 100,
        ),
    ]

    for index, (label, sublabel, value, ratio) in enumerate(metrics):
        x = 0.055 + index * 0.31
        width = 0.26
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.17),
                width,
                0.42,
                boxstyle="round,pad=0.012,rounding_size=0.018",
                linewidth=1,
                edgecolor=LINE,
                facecolor=CARD_ALT,
                transform=ax.transAxes,
            )
        )
        ax.text(x + 0.025, 0.48, label, transform=ax.transAxes, fontsize=9.5, weight="bold", color=TEXT)
        ax.text(x + 0.025, 0.39, sublabel, transform=ax.transAxes, fontsize=7.9, color=MUTED)
        ax.text(x + 0.025, 0.25, value, transform=ax.transAxes, fontsize=17, weight="bold", color=TEXT)
        ax.add_patch(
            FancyBboxPatch(
                (x + 0.025, 0.2),
                width - 0.05,
                0.026,
                boxstyle="round,pad=0,rounding_size=0.008",
                linewidth=0,
                facecolor="#263229",
                transform=ax.transAxes,
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (x + 0.025, 0.2),
                (width - 0.05) * min(max(ratio, 0), 1),
                0.026,
                boxstyle="round,pad=0,rounding_size=0.008",
                linewidth=0,
                facecolor=color,
                transform=ax.transAxes,
            )
        )


def draw_station_frame(station_id: str, categories: pd.DataFrame) -> plt.Figure:
    meta = STATION_FRAMING[station_id]
    station = categories[categories["station_id"] == station_id].iloc[0]

    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    grid = fig.add_gridspec(
        5,
        12,
        height_ratios=[0.72, 1.38, 1.48, 1.48, 0.42],
        hspace=0.34,
        wspace=0.32,
    )

    title_ax = fig.add_subplot(grid[0, :])
    title_ax.axis("off")
    title_ax.add_patch(
        FancyBboxPatch(
            (0, 0.02),
            0.22,
            0.065,
            boxstyle="round,pad=0,rounding_size=0.02",
            linewidth=0,
            facecolor=GREEN,
            transform=title_ax.transAxes,
        )
    )
    title_ax.text(
        0,
        0.72,
        "Station Business Turnover Around Taipei MRT",
        fontsize=28,
        weight="bold",
        color=TEXT,
        transform=title_ax.transAxes,
    )
    title_ax.text(
        0,
        0.24,
        "A three-station loop centered on verified openings and closures, with retail-mix and passenger-flow context",
        fontsize=13,
        color=MUTED,
        transform=title_ax.transAxes,
    )

    station_ax = fig.add_subplot(grid[1, 0:3])
    rounded_panel(station_ax)
    title_size = 17 if len(meta["title"]) > 12 else 24
    subtitle_y = 0.45 if len(meta["title"]) > 12 else 0.55
    note_y = 0.22 if len(meta["title"]) > 12 else 0.29
    add_wrapped_text(
        station_ax,
        0.07,
        0.82,
        meta["title"],
        width=12,
        fontsize=title_size,
        weight="bold",
        color=meta["color"],
    )
    add_wrapped_text(
        station_ax,
        0.07,
        subtitle_y,
        meta["subtitle"],
        width=24,
        fontsize=11.8,
        weight="bold",
        color=TEXT,
    )
    add_wrapped_text(
        station_ax,
        0.07,
        note_y,
        meta["short_note"],
        width=34,
        fontsize=10.2,
        color=MUTED,
    )

    draw_turnover_panel(fig.add_subplot(grid[1:3, 3:8]), station, meta["color"])
    draw_station_comparison(fig.add_subplot(grid[1:3, 8:12]), categories, station_id)

    map_ax = fig.add_subplot(grid[2:4, 0:3])
    rounded_panel(map_ax)
    map_ax.text(0.055, 0.93, "500 m station catchment", transform=map_ax.transAxes, fontsize=14.5, weight="bold", color=TEXT)
    image_ax = map_ax.inset_axes([0.055, 0.07, 0.89, 0.8])
    image_ax.axis("off")
    map_ax.axis("off")
    if meta["map"].exists():
        image_ax.imshow(plt.imread(meta["map"]))
    else:
        image_ax.text(0.5, 0.5, "Map not available", ha="center", va="center", color=MUTED)

    draw_normalized_metrics(fig.add_subplot(grid[3, 3:8]), categories, station_id)

    evidence_ax = fig.add_subplot(grid[3, 8:12])
    rounded_panel(evidence_ax)
    evidence_ax.text(0.055, 0.79, "Evidence status", transform=evidence_ax.transAxes, fontsize=14.5, weight="bold", color=TEXT)
    evidence_ax.text(0.055, 0.59, f"{int(station['total_osm_pois']):,}", transform=evidence_ax.transAxes, fontsize=22, weight="bold", color=meta["color"])
    evidence_ax.text(0.28, 0.625, "mapped places\nproxy retail mix", transform=evidence_ax.transAxes, fontsize=10.2, color=MUTED, va="center")
    evidence_ax.text(0.055, 0.34, f"{int(station['total_station_flow']):,}", transform=evidence_ax.transAxes, fontsize=22, weight="bold", color="#A3FF12")
    evidence_ax.text(0.42, 0.375, "March 2026 station flow\nverified Taipei Metro metric", transform=evidence_ax.transAxes, fontsize=10.2, color=MUTED, va="center")
    add_wrapped_text(
        evidence_ax,
        0.055,
        0.17,
        "2022-present data: city-level context only.",
        width=44,
        fontsize=9.2,
        color=MUTED,
    )

    note_ax = fig.add_subplot(grid[3, :])
    note_ax.axis("off")
    note_ax.remove()

    note_ax = fig.add_subplot(grid[4, :])
    note_ax.axis("off")
    note_ax.text(
        0,
        0.48,
        "Verified station-level: latest monthly business openings/closures and MRT passenger flow. Proxy station-level: OpenStreetMap mapped places and retail category mix.",
        fontsize=10.8,
        color=MUTED,
        transform=note_ax.transAxes,
    )
    return fig


def save_outputs() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    categories = load_inputs()

    frames = []
    for station_id in STATION_ORDER:
        fig = draw_station_frame(station_id, categories)
        frame_path = CHARTS_DIR / f"_station_frontpage_{station_id}.png"
        fig.savefig(frame_path, dpi=100, facecolor=BG)
        plt.close(fig)
        frame = Image.open(frame_path).convert("RGB")
        frame.thumbnail((1050, 591), Image.Resampling.LANCZOS)
        frames.append(frame.copy())
        frame_path.unlink()

    palette_frames = [frame.quantize(colors=96) for frame in frames]
    gif_path = CHARTS_DIR / "mrt_station_retail_dynamics_loop.gif"
    palette_frames[0].save(
        gif_path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=1600,
        loop=0,
        disposal=2,
        optimize=False,
    )

    static_fig = draw_station_frame("zhongshan", categories)
    static_fig.savefig(CHARTS_DIR / "mrt_station_retail_dynamics_frontpage.png", dpi=160, facecolor=BG)
    plt.close(static_fig)


if __name__ == "__main__":
    save_outputs()
