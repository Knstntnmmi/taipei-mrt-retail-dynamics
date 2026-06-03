from pathlib import Path
import textwrap

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
        "color": "#2F7D88",
    },
    "zhongxiao_fuxing": {
        "title": "Zhongxiao Fuxing",
        "subtitle": "Transfer and premium retail node",
        "note": "High passenger flow, but simple point counts understate vertical malls, department stores, and underground retail.",
        "short_note": "High-flow transfer area; vertical malls may be undercounted.",
        "map": MAPS_DIR / "zhongxiao_fuxing_poster_map.png",
        "color": "#8C5A2B",
    },
    "zhongshan": {
        "title": "Zhongshan",
        "subtitle": "Shopping, culture, and tourism node",
        "note": "Largest observed point-of-interest count and highest verified passenger flow among the three stations.",
        "short_note": "Highest latest-month turnover and mapped retail volume.",
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
CATEGORY_SHORT_LABELS = {
    **CATEGORY_LABELS,
    "apparel/fashion": "Fashion",
    "lifestyle/design": "Design",
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
GREEN = "#2E9D68"
RED = "#D86135"
LINE = "#DCE7E3"


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
    ax.add_patch(FancyBboxPatch((0.19, 0.347), 0.67, 0.052, boxstyle="round,pad=0,rounding_size=0.014", linewidth=0, facecolor="#E4EEE9", transform=ax.transAxes))
    ax.add_patch(FancyBboxPatch((0.19, 0.347), 0.67 * openings / max_events, 0.052, boxstyle="round,pad=0,rounding_size=0.014", linewidth=0, facecolor=GREEN, transform=ax.transAxes))
    ax.text(0.89, 0.34, f"{openings}", transform=ax.transAxes, fontsize=11, weight="bold", color=TEXT)

    ax.text(0.055, 0.25, "Close", transform=ax.transAxes, fontsize=10.5, color=MUTED)
    ax.add_patch(FancyBboxPatch((0.19, 0.257), 0.67, 0.052, boxstyle="round,pad=0,rounding_size=0.014", linewidth=0, facecolor="#F3E2DD", transform=ax.transAxes))
    ax.add_patch(FancyBboxPatch((0.19, 0.257), 0.67 * closures / max_events, 0.052, boxstyle="round,pad=0,rounding_size=0.014", linewidth=0, facecolor=RED, transform=ax.transAxes))
    ax.text(0.89, 0.25, f"{closures}", transform=ax.transAxes, fontsize=11, weight="bold", color=TEXT)

    ax.text(0.055, 0.115, f"{closure_rate:.2f}% closure rate ({total_events} latest-month events)", transform=ax.transAxes, fontsize=11.5, weight="bold", color=TEXT)
    ax.text(0.055, 0.055, "Verified station-level evidence; not a full 2022-present station history.", transform=ax.transAxes, fontsize=10, color=MUTED)


def draw_station_comparison(ax, categories: pd.DataFrame, station_id: str) -> None:
    ax.axis("off")
    rounded_panel(ax)
    ax.text(0.055, 0.91, "Three-station turnover ranking", transform=ax.transAxes, fontsize=15, weight="bold", color=TEXT)
    ax.text(0.055, 0.845, "Latest official station-level events", transform=ax.transAxes, fontsize=10, color=MUTED)
    max_poi = categories["total_osm_pois"].max()
    max_flow = categories["total_station_flow"].max()
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
        color = STATION_FRAMING[compare_id]["color"] if active else "#A9B7BC"
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
                facecolor="#DDE7E4",
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
        ax.text(0.055, y - 0.045, f"{int(row['total_osm_pois']):,} mapped places", transform=ax.transAxes, fontsize=9.1, color=MUTED)
        ax.add_patch(
            FancyBboxPatch(
                (0.43, y - 0.025),
                0.48,
                0.035,
                boxstyle="round,pad=0,rounding_size=0.01",
                linewidth=0,
                facecolor="#DDE7E4",
                transform=ax.transAxes,
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (0.43, y - 0.025),
                0.48 * row["total_station_flow"] / max_flow,
                0.035,
                boxstyle="round,pad=0,rounding_size=0.01",
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
    station_ax.text(0.07, 0.82, meta["title"], fontsize=24, weight="bold", color=meta["color"], transform=station_ax.transAxes, va="top")
    add_wrapped_text(station_ax, 0.07, 0.55, meta["subtitle"], width=24, fontsize=11.8, weight="bold", color=TEXT)
    add_wrapped_text(station_ax, 0.07, 0.29, meta["short_note"], width=34, fontsize=10.2, color=MUTED)

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

    category_cols = list(CATEGORY_LABELS)
    values = pd.Series({col: station[col] for col in category_cols}).sort_values(ascending=True).tail(6)
    bar_ax = fig.add_subplot(grid[3, 3:8])
    bar_ax.set_facecolor(CARD)
    bar_ax.barh(
        [CATEGORY_SHORT_LABELS[col] for col in values.index],
        values.values,
        color=[CATEGORY_COLORS[col] for col in values.index],
    )
    bar_ax.set_title("Top mapped retail categories", loc="left", fontsize=14.5, weight="bold", color=TEXT, pad=10)
    bar_ax.set_xlabel("OpenStreetMap mapped places", color=MUTED)
    bar_ax.tick_params(axis="both", colors=MUTED, labelsize=9.5)
    bar_ax.grid(axis="x", color="#DDE7E4", linewidth=0.8)
    for spine in bar_ax.spines.values():
        spine.set_visible(False)
    for y, value in enumerate(values.values):
        bar_ax.text(value + 4, y, f"{int(value):,}", va="center", fontsize=9.5, color=TEXT)
    bar_ax.set_xlim(0, max(values.max() * 1.18, 120))

    evidence_ax = fig.add_subplot(grid[3, 8:12])
    rounded_panel(evidence_ax)
    evidence_ax.text(0.055, 0.79, "Evidence status", transform=evidence_ax.transAxes, fontsize=14.5, weight="bold", color=TEXT)
    evidence_ax.text(0.055, 0.59, f"{int(station['total_osm_pois']):,}", transform=evidence_ax.transAxes, fontsize=22, weight="bold", color=meta["color"])
    evidence_ax.text(0.28, 0.625, "mapped places\nproxy retail mix", transform=evidence_ax.transAxes, fontsize=10.2, color=MUTED, va="center")
    evidence_ax.text(0.055, 0.34, f"{int(station['total_station_flow']):,}", transform=evidence_ax.transAxes, fontsize=22, weight="bold", color="#247BA0")
    evidence_ax.text(0.42, 0.375, "March 2026 station flow\nverified Taipei Metro metric", transform=evidence_ax.transAxes, fontsize=10.2, color=MUTED, va="center")
    add_wrapped_text(
        evidence_ax,
        0.055,
        0.085,
        "2022-present opening/closure history remains city-level context until a full station-geocoded panel is available.",
        width=58,
        fontsize=9.4,
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
        frame.thumbnail((1200, 675), Image.Resampling.LANCZOS)
        frames.append(frame.copy())
        frame_path.unlink()

    smooth_frames = []
    hold_frames = 8
    transition_frames = 8
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
        optimize=False,
    )

    static_fig = draw_station_frame("zhongshan", categories)
    static_fig.savefig(CHARTS_DIR / "mrt_station_retail_dynamics_frontpage.png", dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close(static_fig)


if __name__ == "__main__":
    save_outputs()
