from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyBboxPatch
from PIL import Image, ImageSequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"


FOCUS_CATEGORIES = ["shop/retail", "food/cafe", "services", "lifestyle/culture"]
CATEGORY_LABELS = {
    "shop/retail": "Shop / retail",
    "food/cafe": "Food / cafe",
    "services": "Services",
    "lifestyle/culture": "Lifestyle / culture",
}
COLORS = {
    "shop/retail": "#247BA0",
    "food/cafe": "#F25F5C",
    "services": "#70C1B3",
    "lifestyle/culture": "#F3B23A",
}
OPEN_COLOR = "#2E9D68"
CLOSE_COLOR = "#D86135"
TEXT = "#1B2A2F"
MUTED = "#60737A"
BG = "#F7FAF9"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    yearly = pd.read_csv(TABLES_DIR / "taipei_business_open_close_percentages_by_category_2022_2025.csv")
    all_totals = pd.read_csv(TABLES_DIR / "taipei_business_open_close_category_totals_2022_2025.csv")
    totals = all_totals[all_totals["analysis_category"].isin(FOCUS_CATEGORIES)].copy()
    yearly = yearly[yearly["analysis_category"].isin(FOCUS_CATEGORIES)].copy()
    yearly["label"] = yearly["analysis_category"].map(CATEGORY_LABELS)
    totals["label"] = totals["analysis_category"].map(CATEGORY_LABELS)
    return yearly, totals, all_totals


def setup_axis(ax, title: str) -> None:
    ax.set_facecolor("white")
    ax.grid(axis="x", color="#DDE7E4", linewidth=0.8)
    ax.set_title(title, loc="left", fontsize=17, weight="bold", color=TEXT, pad=12)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="both", colors=MUTED, labelsize=11)


def draw_kpi(ax, x: float, y: float, label: str, value: str, color: str) -> None:
    card = FancyBboxPatch(
        (x, y),
        0.28,
        0.24,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=0,
        facecolor="white",
        transform=ax.transAxes,
    )
    ax.add_patch(card)
    ax.text(x + 0.018, y + 0.125, value, transform=ax.transAxes, fontsize=20, weight="bold", color=color)
    ax.text(x + 0.018, y + 0.045, label, transform=ax.transAxes, fontsize=10.5, color=MUTED)


def draw_frame(
    frame_year: int,
    fig,
    axes,
    yearly: pd.DataFrame,
    totals: pd.DataFrame,
    all_totals: pd.DataFrame,
) -> None:
    for ax in axes:
        ax.clear()

    ax_title, ax_open, ax_close, ax_net = axes
    ax_title.axis("off")
    current = yearly[yearly["year"] <= frame_year]
    year_slice = yearly[yearly["year"] == frame_year].copy()
    total_slice = totals.copy()

    open_total = int(current["openings"].sum())
    close_total = int(current["closures"].sum())
    net_total = open_total - close_total
    retail_food = all_totals[all_totals["analysis_category"].isin(["shop/retail", "food/cafe"])]
    opening_share = retail_food["openings"].sum() / all_totals["openings"].sum() * 100
    closure_share = retail_food["closures"].sum() / all_totals["closures"].sum() * 100

    fig.suptitle(
        "Taipei Business Opening and Closing Dynamics",
        x=0.055,
        y=0.955,
        ha="left",
        fontsize=26,
        weight="bold",
        color=TEXT,
    )
    ax_title.text(
        0.01,
        0.73,
        f"Official Taipei city industry data, 2022-{frame_year}",
        transform=ax_title.transAxes,
        fontsize=16,
        color=MUTED,
    )
    ax_title.text(
        0.01,
        0.52,
        "Used as verified city-level turnover context. Station-buffer POIs remain separate proxy metrics.",
        transform=ax_title.transAxes,
        fontsize=12.5,
        color=MUTED,
    )
    ax_title.text(
        0.01,
        0.36,
        f"Shop/retail + food/cafe = {opening_share:.1f}% of openings and {closure_share:.1f}% of closures.",
        transform=ax_title.transAxes,
        fontsize=12.2,
        color=TEXT,
        weight="bold",
    )
    draw_kpi(ax_title, 0.01, 0.02, "Openings accumulated", f"{open_total:,}", OPEN_COLOR)
    draw_kpi(ax_title, 0.33, 0.02, "Closures accumulated", f"{close_total:,}", CLOSE_COLOR)
    draw_kpi(ax_title, 0.65, 0.02, "Net change", f"{net_total:+,}", "#247BA0")

    ordered = year_slice.sort_values("openings", ascending=True)
    setup_axis(ax_open, f"Openings in {frame_year}")
    ax_open.barh(ordered["label"], ordered["openings"], color=[COLORS[c] for c in ordered["analysis_category"]])
    ax_open.set_xlabel("New business registrations", color=MUTED)
    ax_open.set_xlim(0, max(3000, yearly["openings"].max() * 1.15))
    for y, value in enumerate(ordered["openings"]):
        ax_open.text(value + 60, y, f"{int(value):,}", va="center", fontsize=11, color=TEXT)

    ordered_close = year_slice.sort_values("closures", ascending=True)
    setup_axis(ax_close, f"Closures in {frame_year}")
    ax_close.barh(ordered_close["label"], ordered_close["closures"], color=[COLORS[c] for c in ordered_close["analysis_category"]])
    ax_close.set_xlabel("Business closure registrations", color=MUTED)
    ax_close.set_xlim(0, max(3000, yearly["closures"].max() * 1.15))
    for y, value in enumerate(ordered_close["closures"]):
        ax_close.text(value + 60, y, f"{int(value):,}", va="center", fontsize=11, color=TEXT)

    total_focus = totals.sort_values("open_plus_close", ascending=True)
    setup_axis(ax_net, "2022-2025 turnover pressure")
    ax_net.barh(total_focus["label"], total_focus["openings"], color=OPEN_COLOR, alpha=0.85, label="Openings")
    ax_net.barh(total_focus["label"], -total_focus["closures"], color=CLOSE_COLOR, alpha=0.85, label="Closures")
    ax_net.axvline(0, color=TEXT, linewidth=1)
    ax_net.set_xlabel("Openings vs. closures", color=MUTED)
    max_abs = max(total_focus["openings"].max(), total_focus["closures"].max()) * 1.2
    ax_net.set_xlim(-max_abs, max_abs)
    ax_net.legend(loc="lower right", frameon=False, fontsize=10)

def save_animation() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    yearly, totals, all_totals = load_data()
    years = sorted(yearly["year"].unique())

    fig = plt.figure(figsize=(14, 8), facecolor=BG)
    gs = fig.add_gridspec(3, 2, height_ratios=[1.05, 1.35, 1.45], hspace=0.52, wspace=0.26)
    axes = [
        fig.add_subplot(gs[0, :]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1]),
        fig.add_subplot(gs[2, :]),
    ]

    frames = years + [years[-1]] * 8
    gif_path = CHARTS_DIR / "business_open_close_animated_dashboard.gif"
    animation = FuncAnimation(fig, draw_frame, frames=frames, fargs=(fig, axes, yearly, totals, all_totals), interval=850)
    animation.save(gif_path, writer=PillowWriter(fps=1.2), dpi=130)
    force_infinite_gif_loop(gif_path)
    draw_frame(years[-1], fig, axes, yearly, totals, all_totals)
    fig.savefig(CHARTS_DIR / "business_open_close_dashboard.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def force_infinite_gif_loop(gif_path: Path) -> None:
    with Image.open(gif_path) as image:
        frames = [frame.copy() for frame in ImageSequence.Iterator(image)]
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=830,
        loop=0,
        disposal=2,
    )


if __name__ == "__main__":
    save_animation()
