from pathlib import Path

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
        "map": MAPS_DIR / "gongguan_poster_map.png",
        "color": "#2F7D88",
    },
    "zhongxiao_fuxing": {
        "title": "Zhongxiao Fuxing",
        "subtitle": "Transfer and premium retail node",
        "note": "High passenger flow, but simple point counts understate vertical malls, department stores, and underground retail.",
        "map": MAPS_DIR / "zhongxiao_fuxing_poster_map.png",
        "color": "#8C5A2B",
    },
    "zhongshan": {
        "title": "Zhongshan",
        "subtitle": "Shopping, culture, and tourism node",
        "note": "Largest observed point-of-interest count and highest verified passenger flow among the three stations.",
        "map": MAPS_DIR / "zhongshan_poster_map.png",
        "color": "#6A6FA8",
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
CATEGORY_COLORS = {
    "food": "#E76F51",
    "cafe": "#F4A261",
    "convenience": "#2A9D8F",
    "apparel/fashion": "#6A6FA8",
    "lifestyle/design": "#C65FA7",
    "education": "#E9C46A",
    "health": "#4F9D69",
    "services": "#457B9D",
    "other": "#8D99AE",
}

TEXT = "#1B2A2F"
MUTED = "#65777E"
BG = "#F6FAF9"
CARD = "white"
def load_inputs() -> pd.DataFrame:
    categories = pd.read_csv(TABLES_DIR / "retail_category_count_by_station.csv")
    totals = pd.read_csv(TABLES_DIR / "total_poi_count_by_station.csv")
    flow = pd.read_csv(TABLES_DIR / "mrt_passenger_flow_by_station.csv")
    events = pd.read_csv(TABLES_DIR / "station_business_open_close_latest_month_summary.csv")

    categories = categories.merge(totals[["station_id", "total_osm_pois"]], on="station_id")
    categories = categories.merge(flow[["station_id", "total_station_flow"]], on="station_id")
    categories = categories.merge(
        events[["station_id", "event_month", "openings", "closures", "net_change"]],
        on="station_id",
        how="left",
    )
    categories[["openings", "closures", "net_change"]] = categories[
        ["openings", "closures", "net_change"]
    ].fillna(0).astype(int)
    categories["event_month"] = categories["event_month"].fillna("latest month")
    return categories


def draw_card(ax, title: str, value: str, subtitle: str, color: str) -> None:
    ax.axis("off")
    ax.add_patch(
        FancyBboxPatch(
            (0.02, 0.1),
            0.96,
            0.8,
            boxstyle="round,pad=0.018,rounding_size=0.025",
            linewidth=0,
            facecolor=CARD,
            transform=ax.transAxes,
        )
    )
    value_size = 18 if "/" in value else 22
    ax.text(0.07, 0.58, value, transform=ax.transAxes, fontsize=value_size, weight="bold", color=color)
    ax.text(0.08, 0.33, title, transform=ax.transAxes, fontsize=10.5, weight="bold", color=TEXT)
    ax.text(0.08, 0.18, subtitle, transform=ax.transAxes, fontsize=9.2, color=MUTED)


def draw_station_comparison(ax, categories: pd.DataFrame, station_id: str) -> None:
    ax.axis("off")
    ax.set_title("Three-station comparison", loc="left", fontsize=15, weight="bold", color=TEXT, pad=10)
    max_poi = categories["total_osm_pois"].max()
    max_flow = categories["total_station_flow"].max()
    labels = {
        "gongguan": "Gongguan",
        "zhongxiao_fuxing": "Zhongxiao Fuxing",
        "zhongshan": "Zhongshan",
    }
    for index, compare_id in enumerate(STATION_ORDER):
        row = categories[categories["station_id"] == compare_id].iloc[0]
        y = 0.78 - index * 0.28
        active = compare_id == station_id
        color = STATION_FRAMING[compare_id]["color"] if active else "#A9B7BC"
        text_color = TEXT if active else MUTED
        ax.text(0.02, y + 0.08, labels[compare_id], transform=ax.transAxes, fontsize=11.5, weight="bold", color=text_color)
        ax.text(0.02, y - 0.005, f"{int(row['total_osm_pois']):,} mapped places", transform=ax.transAxes, fontsize=9.2, color=MUTED)
        ax.add_patch(
            FancyBboxPatch(
                (0.45, y + 0.04),
                0.48,
                0.055,
                boxstyle="round,pad=0,rounding_size=0.01",
                linewidth=0,
                facecolor="#DDE7E4",
                transform=ax.transAxes,
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (0.45, y + 0.04),
                0.48 * row["total_osm_pois"] / max_poi,
                0.055,
                boxstyle="round,pad=0,rounding_size=0.01",
                linewidth=0,
                facecolor=color,
                transform=ax.transAxes,
            )
        )
        ax.text(0.02, y - 0.09, f"{int(row['total_station_flow']):,} passenger flow", transform=ax.transAxes, fontsize=9.2, color=MUTED)
        ax.add_patch(
            FancyBboxPatch(
                (0.45, y - 0.07),
                0.48,
                0.055,
                boxstyle="round,pad=0,rounding_size=0.01",
                linewidth=0,
                facecolor="#DDE7E4",
                transform=ax.transAxes,
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (0.45, y - 0.07),
                0.48 * row["total_station_flow"] / max_flow,
                0.055,
                boxstyle="round,pad=0,rounding_size=0.01",
                linewidth=0,
                facecolor=color,
                transform=ax.transAxes,
            )
        )


def draw_station_frame(station_id: str, categories: pd.DataFrame) -> plt.Figure:
    meta = STATION_FRAMING[station_id]
    station = categories[categories["station_id"] == station_id].iloc[0]

    fig = plt.figure(figsize=(15.5, 8.5), facecolor=BG)
    grid = fig.add_gridspec(
        4,
        8,
        height_ratios=[0.75, 1.0, 2.35, 0.58],
        width_ratios=[1.1, 1.1, 1.1, 1, 1, 1, 1, 1],
        hspace=0.35,
        wspace=0.36,
    )

    title_ax = fig.add_subplot(grid[0, :])
    title_ax.axis("off")
    title_ax.text(
        0,
        0.72,
        "Taipei MRT Retail Dynamics",
        fontsize=30,
        weight="bold",
        color=TEXT,
        transform=title_ax.transAxes,
    )
    title_ax.text(
        0,
        0.24,
        "Station-by-station loop for Gongguan, Zhongxiao Fuxing, and Zhongshan: retail mix, passenger flow, and latest business events",
        fontsize=13,
        color=MUTED,
        transform=title_ax.transAxes,
    )

    station_ax = fig.add_subplot(grid[1, 0:3])
    station_ax.axis("off")
    station_ax.add_patch(
        FancyBboxPatch(
            (0.01, 0.08),
            0.98,
            0.84,
            boxstyle="round,pad=0.02,rounding_size=0.028",
            linewidth=0,
            facecolor=CARD,
            transform=station_ax.transAxes,
        )
    )
    station_ax.text(0.055, 0.58, meta["title"], fontsize=24, weight="bold", color=meta["color"], transform=station_ax.transAxes)
    station_ax.text(0.055, 0.31, meta["subtitle"], fontsize=12.5, color=TEXT, transform=station_ax.transAxes)

    draw_card(
        fig.add_subplot(grid[1, 3:5]),
        "Current mapped places",
        f"{int(station['total_osm_pois']):,}",
        "OpenStreetMap points of interest",
        meta["color"],
    )
    draw_card(
        fig.add_subplot(grid[1, 5:7]),
        "March 2026 station flow",
        f"{int(station['total_station_flow']):,}",
        "Taipei Metro entries + exits",
        "#247BA0",
    )
    top_category = max(CATEGORY_LABELS, key=lambda col: station[col])
    draw_card(
        fig.add_subplot(grid[1, 7:8]),
        "Latest station events",
        f"+{int(station['openings'])} / -{int(station['closures'])}",
        f"{station['event_month']} openings / closures",
        "#2E9D68" if station["net_change"] >= 0 else "#D86135",
    )

    map_ax = fig.add_subplot(grid[2, 0:3])
    map_ax.set_title("500 m station catchment map", loc="left", fontsize=15, weight="bold", color=TEXT, pad=10)
    map_ax.axis("off")
    if meta["map"].exists():
        map_ax.imshow(plt.imread(meta["map"]))
    else:
        map_ax.text(0.5, 0.5, "Map not available", ha="center", va="center", color=MUTED)

    category_cols = list(CATEGORY_LABELS)
    values = pd.Series({col: station[col] for col in category_cols}).sort_values(ascending=True)
    bar_ax = fig.add_subplot(grid[2, 3:6])
    bar_ax.set_facecolor(CARD)
    bar_ax.barh(
        [CATEGORY_LABELS[col] for col in values.index],
        values.values,
        color=[CATEGORY_COLORS[col] for col in values.index],
    )
    bar_ax.set_title("Retail mix inside the station area", loc="left", fontsize=15, weight="bold", color=TEXT, pad=10)
    bar_ax.set_xlabel("Mapped places", color=MUTED)
    bar_ax.tick_params(axis="both", colors=MUTED, labelsize=9.5)
    bar_ax.grid(axis="x", color="#DDE7E4", linewidth=0.8)
    for spine in bar_ax.spines.values():
        spine.set_visible(False)
    for y, value in enumerate(values.values):
        bar_ax.text(value + 4, y, f"{int(value):,}", va="center", fontsize=9.5, color=TEXT)
    bar_ax.set_xlim(0, max(values.max() * 1.18, 120))

    comparison_ax = fig.add_subplot(grid[2, 6:8])
    draw_station_comparison(comparison_ax, categories, station_id)

    note_ax = fig.add_subplot(grid[3, :])
    note_ax.axis("off")
    note_ax.text(0, 0.62, meta["note"], fontsize=12, color=TEXT, transform=note_ax.transAxes)
    note_ax.text(
        0,
        0.18,
        "Important: mapped places are OpenStreetMap proxy data. Passenger flow and latest monthly business openings/closures are verified station-level data.",
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
        fig.savefig(frame_path, dpi=135, facecolor=BG)
        plt.close(fig)
        frames.append(Image.open(frame_path).convert("RGB"))
        frame_path.unlink()

    smooth_frames = []
    hold_frames = 10
    transition_frames = 14
    for index, frame in enumerate(frames):
        next_frame = frames[(index + 1) % len(frames)]
        smooth_frames.extend([frame.copy() for _ in range(hold_frames)])
        for step in range(1, transition_frames + 1):
            amount = step / (transition_frames + 1)
            smooth_frames.append(Image.blend(frame, next_frame, amount))

    palette_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE) for frame in smooth_frames]
    gif_path = CHARTS_DIR / "mrt_station_retail_dynamics_loop.gif"
    palette_frames[0].save(
        gif_path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=85,
        loop=0,
        disposal=2,
        optimize=True,
    )

    static_fig = draw_station_frame("zhongshan", categories)
    static_fig.savefig(CHARTS_DIR / "mrt_station_retail_dynamics_frontpage.png", dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close(static_fig)


if __name__ == "__main__":
    save_outputs()
