from pathlib import Path

import pandas as pd
import qrcode
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A1
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "poster"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

POSTER_PDF = OUTPUT_DIR / "nccu_innofest_taipei_mrt_retail_dynamics_a1_poster.pdf"
POSTER_PREVIEW = OUTPUT_DIR / "nccu_innofest_taipei_mrt_retail_dynamics_a1_poster_preview.png"
QR_PATH = OUTPUT_DIR / "github_qr.png"

GITHUB_URL = "https://github.com/Knstntnmmi/taipei-mrt-retail-dynamics"

PAGE_W, PAGE_H = A1  # portrait: 59.4 cm x 84.1 cm
MARGIN = 1.45 * cm
GUTTER = 0.65 * cm


PALETTE = {
    "ink": colors.HexColor("#172026"),
    "muted": colors.HexColor("#52636d"),
    "line": colors.HexColor("#d7e0df"),
    "paper": colors.HexColor("#f7faf8"),
    "white": colors.white,
    "teal": colors.HexColor("#1f6f78"),
    "green": colors.HexColor("#2d8a62"),
    "orange": colors.HexColor("#d66a2f"),
    "blue": colors.HexColor("#386fa4"),
    "pale_teal": colors.HexColor("#e9f3f2"),
    "pale_green": colors.HexColor("#edf6ef"),
    "pale_orange": colors.HexColor("#fff1e9"),
}


styles = getSampleStyleSheet()
BODY = ParagraphStyle(
    "PosterBody",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=16,
    leading=20,
    textColor=PALETTE["ink"],
    alignment=TA_LEFT,
)
SMALL = ParagraphStyle(
    "PosterSmall",
    parent=BODY,
    fontSize=12.5,
    leading=15.5,
    textColor=PALETTE["muted"],
)
TITLE = ParagraphStyle(
    "PosterTitle",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=50,
    leading=56,
    textColor=colors.white,
)
SUBTITLE = ParagraphStyle(
    "PosterSubtitle",
    parent=BODY,
    fontSize=22,
    leading=27,
    textColor=colors.HexColor("#dff1ef"),
)
SECTION = ParagraphStyle(
    "PosterSection",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=26,
    textColor=PALETTE["teal"],
)
CALLOUT = ParagraphStyle(
    "PosterCallout",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=15,
    leading=18,
    textColor=PALETTE["ink"],
)
STATION_TITLE = ParagraphStyle(
    "StationTitle",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=21,
    textColor=PALETTE["teal"],
)
TINY = ParagraphStyle(
    "PosterTiny",
    parent=SMALL,
    fontSize=9.5,
    leading=11.5,
)

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


def mm(value):
    return value / 10 * cm


def top_y(y_from_top):
    return PAGE_H - y_from_top


def draw_para(c, text, x, y_top, width, height, style=BODY):
    para = Paragraph(text, style)
    para.wrapOn(c, width, height)
    para.drawOn(c, x, top_y(y_top) - height)


def draw_section_title(c, title, x, y_top, width):
    c.setFillColor(PALETTE["teal"])
    c.roundRect(x, top_y(y_top + 7), width, 0.35 * cm, 0.16 * cm, fill=1, stroke=0)
    draw_para(c, title, x, y_top + 13, width, 0.75 * cm, SECTION)


def draw_card(c, x, y_top, w, h, title, value, note, fill_color):
    y = top_y(y_top + h)
    c.setFillColor(fill_color)
    c.setStrokeColor(PALETTE["line"])
    c.roundRect(x, y, w, h, 0.22 * cm, fill=1, stroke=1)
    draw_para(c, title, x + 0.45 * cm, y_top + 0.42 * cm, w - 0.9 * cm, 0.55 * cm, SMALL)
    c.setFillColor(PALETTE["ink"])
    c.setFont("Helvetica-Bold", 31)
    c.drawString(x + 0.45 * cm, y + h - 1.9 * cm, value)
    draw_para(c, note, x + 0.45 * cm, y_top + 2.45 * cm, w - 0.9 * cm, h - 2.7 * cm, SMALL)


def draw_box(c, x, y_top, w, h, title, body, fill=PALETTE["white"]):
    y = top_y(y_top + h)
    c.setFillColor(fill)
    c.setStrokeColor(PALETTE["line"])
    c.roundRect(x, y, w, h, 0.24 * cm, fill=1, stroke=1)
    draw_section_title(c, title, x + 0.5 * cm, y_top + 0.35 * cm, w - 1 * cm)
    draw_para(c, body, x + 0.55 * cm, y_top + 1.55 * cm, w - 1.1 * cm, h - 1.85 * cm, BODY)


def draw_image_panel(c, x, y_top, w, h, title, image_path, note=None):
    y = top_y(y_top + h)
    c.setFillColor(PALETTE["white"])
    c.setStrokeColor(PALETTE["line"])
    c.roundRect(x, y, w, h, 0.24 * cm, fill=1, stroke=1)
    draw_section_title(c, title, x + 0.5 * cm, y_top + 0.35 * cm, w - 1 * cm)
    image_box_y_top = y_top + 1.45 * cm
    image_box_h = h - 2.15 * cm if note else h - 1.85 * cm
    img = Image.open(image_path)
    iw, ih = img.size
    scale = min((w - 1.0 * cm) / iw, image_box_h / ih)
    draw_w, draw_h = iw * scale, ih * scale
    draw_x = x + (w - draw_w) / 2
    draw_y = top_y(image_box_y_top + image_box_h) + (image_box_h - draw_h) / 2
    c.drawImage(str(image_path), draw_x, draw_y, draw_w, draw_h, preserveAspectRatio=True, mask="auto")
    if note:
        draw_para(c, note, x + 0.55 * cm, y_top + h - 0.65 * cm, w - 1.1 * cm, 0.48 * cm, SMALL)


def create_station_profile_maps():
    import geopandas as gpd
    import matplotlib.pyplot as plt

    map_dir = OUTPUT_DIR / "station_profile_maps"
    map_dir.mkdir(parents=True, exist_ok=True)
    pois = gpd.read_file(PROJECT_ROOT / "data" / "raw" / "osm_pois_within_500m.geojson").to_crs("EPSG:3826")
    buffers = gpd.read_file(PROJECT_ROOT / "outputs" / "buffers" / "mrt_station_500m_buffers.geojson").to_crs("EPSG:3826")

    paths = {}
    for station_id, station_pois in pois.groupby("station_id"):
        station_buffer = buffers[buffers["station_id"] == station_id]
        fig, ax = plt.subplots(figsize=(5.4, 4.15), dpi=220)
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        station_buffer.boundary.plot(ax=ax, linewidth=2.0, color="#172026")

        for category, color in CATEGORY_COLORS.items():
            subset = station_pois[station_pois["retail_category"] == category]
            if not subset.empty:
                subset.plot(ax=ax, markersize=7, color=color, alpha=0.82)

        minx, miny, maxx, maxy = station_buffer.total_bounds
        pad = 80
        ax.set_xlim(minx - pad, maxx + pad)
        ax.set_ylim(miny - pad, maxy + pad)
        ax.set_aspect("equal")
        ax.axis("off")
        out = map_dir / f"{station_id}_poster_map.png"
        fig.savefig(out, bbox_inches="tight", pad_inches=0.03)
        plt.close(fig)
        paths[station_id] = out
    return paths


def draw_stat_chip(c, x, y_top, w, label, value, fill):
    y = top_y(y_top + 1.35 * cm)
    c.setFillColor(fill)
    c.setStrokeColor(PALETTE["line"])
    c.roundRect(x, y, w, 1.35 * cm, 0.16 * cm, fill=1, stroke=1)
    draw_para(c, label, x + 0.22 * cm, y_top + 0.16 * cm, w - 0.44 * cm, 0.34 * cm, TINY)
    c.setFillColor(PALETTE["ink"])
    c.setFont("Helvetica-Bold", 13.5)
    c.drawString(x + 0.22 * cm, y + 0.28 * cm, value)


def draw_station_profile_panel(c, x, y_top, w, h, title, map_path, stats, insight):
    y = top_y(y_top + h)
    c.setFillColor(PALETTE["white"])
    c.setStrokeColor(PALETTE["line"])
    c.roundRect(x, y, w, h, 0.24 * cm, fill=1, stroke=1)

    c.setFillColor(PALETTE["teal"])
    c.roundRect(x + 0.5 * cm, top_y(y_top + 0.72 * cm), w - 1.0 * cm, 0.28 * cm, 0.14 * cm, fill=1, stroke=0)
    draw_para(c, title, x + 0.5 * cm, y_top + 0.9 * cm, w - 1.0 * cm, 0.62 * cm, STATION_TITLE)

    map_x = x + 0.45 * cm
    map_y_top = y_top + 1.85 * cm
    map_w = w * 0.57
    map_h = 7.05 * cm
    img = Image.open(map_path)
    iw, ih = img.size
    scale = min(map_w / iw, map_h / ih)
    draw_w, draw_h = iw * scale, ih * scale
    c.drawImage(
        str(map_path),
        map_x + (map_w - draw_w) / 2,
        top_y(map_y_top + map_h) + (map_h - draw_h) / 2,
        draw_w,
        draw_h,
        preserveAspectRatio=True,
        mask="auto",
    )

    chip_x = x + w * 0.61
    chip_w = w * 0.35
    chip_y = y_top + 2.05 * cm
    chip_fills = [PALETTE["pale_teal"], PALETTE["pale_green"], PALETTE["pale_orange"]]
    for i, (label, value) in enumerate(stats):
        draw_stat_chip(c, chip_x, chip_y + i * 1.65 * cm, chip_w, label, value, chip_fills[i])

    legend_y = y_top + 7.35 * cm
    legend_items = [("food", CATEGORY_COLORS["food"]), ("services", CATEGORY_COLORS["services"]), ("cafe", CATEGORY_COLORS["cafe"]), ("other", CATEGORY_COLORS["other"])]
    for i, (label, color) in enumerate(legend_items):
        lx = chip_x + (i % 2) * (chip_w / 2)
        ly = legend_y + (i // 2) * 0.42 * cm
        c.setFillColor(colors.HexColor(color))
        c.circle(lx + 0.08 * cm, top_y(ly) - 0.06 * cm, 0.055 * cm, fill=1, stroke=0)
        draw_para(c, label, lx + 0.2 * cm, ly - 0.19 * cm, chip_w / 2 - 0.25 * cm, 0.28 * cm, TINY)

    draw_para(c, insight, x + 0.55 * cm, y_top + 9.15 * cm, w - 1.1 * cm, 2.85 * cm, SMALL)


def make_table(data, column_widths, font_size=12.5):
    table = Table(data, colWidths=column_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PALETTE["teal"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("LEADING", (0, 0), (-1, -1), font_size + 2),
                ("GRID", (0, 0), (-1, -1), 0.35, PALETTE["line"]),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALETTE["pale_teal"]]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def draw_table_panel(c, x, y_top, w, h, title, table):
    y = top_y(y_top + h)
    c.setFillColor(PALETTE["white"])
    c.setStrokeColor(PALETTE["line"])
    c.roundRect(x, y, w, h, 0.24 * cm, fill=1, stroke=1)
    draw_section_title(c, title, x + 0.5 * cm, y_top + 0.35 * cm, w - 1 * cm)
    table_w, table_h = table.wrapOn(c, w - 1.0 * cm, h - 1.7 * cm)
    table.drawOn(c, x + 0.5 * cm, top_y(y_top + 1.55 * cm) - table_h)


def fmt_int(value):
    return f"{int(value):,}"


def generate_qr():
    qr = qrcode.QRCode(border=1, box_size=12)
    qr.add_data(GITHUB_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#172026", back_color="white").convert("RGB")
    img.save(QR_PATH)


def build_poster():
    generate_qr()
    station_map_paths = create_station_profile_maps()

    total = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "total_poi_count_by_station.csv")
    flow = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "mrt_passenger_flow_by_station.csv")
    exits = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "mrt_exit_count_by_station.csv")
    category_counts = pd.read_csv(PROJECT_ROOT / "outputs" / "tables" / "retail_category_count_by_station.csv")

    c = canvas.Canvas(str(POSTER_PDF), pagesize=A1)
    c.setTitle("NCCU Innofest Poster - Taipei MRT Retail Dynamics")

    # Background and header
    c.setFillColor(PALETTE["paper"])
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(PALETTE["teal"])
    c.rect(0, PAGE_H - 8.6 * cm, PAGE_W, 8.6 * cm, fill=1, stroke=0)
    c.setFillColor(PALETTE["green"])
    c.rect(0, PAGE_H - 8.6 * cm, PAGE_W, 0.45 * cm, fill=1, stroke=0)

    draw_para(c, "Taipei MRT Retail Dynamics", MARGIN, 1.05 * cm, PAGE_W - 2 * MARGIN, 1.55 * cm, TITLE)
    draw_para(
        c,
        "A reproducible spatial data science comparison of Gongguan, Zhongxiao Fuxing, and Zhongshan",
        MARGIN,
        3.05 * cm,
        PAGE_W - 2 * MARGIN,
        0.95 * cm,
        SUBTITLE,
    )
    draw_para(
        c,
        "Group 12 | NCCU Innofest 2026 | Analytical unit: 500 m MRT station catchments",
        MARGIN,
        4.15 * cm,
        PAGE_W - 2 * MARGIN,
        0.8 * cm,
        ParagraphStyle("HeaderMeta", parent=SUBTITLE, fontSize=15, leading=19),
    )
    draw_para(
        c,
        "<b>Research question:</b> How do retail density, retail mix, catchment definition, and MRT passenger flow differ across three Taipei MRT station areas?",
        MARGIN,
        5.45 * cm,
        PAGE_W - 2 * MARGIN - 5.5 * cm,
        1.5 * cm,
        ParagraphStyle("Question", parent=SUBTITLE, fontSize=18, leading=22),
    )

    c.drawImage(str(QR_PATH), PAGE_W - MARGIN - 4.7 * cm, PAGE_H - 7.1 * cm, 4.2 * cm, 4.2 * cm, mask="auto")
    draw_para(
        c,
        "GitHub repo<br/>code, data, maps",
        PAGE_W - MARGIN - 4.9 * cm,
        6.95 * cm,
        4.8 * cm,
        1.0 * cm,
        ParagraphStyle("QRLabel", parent=SUBTITLE, fontSize=10.5, leading=12, alignment=1),
    )

    # Metric cards
    card_y = 9.35 * cm
    card_h = 3.9 * cm
    card_w = (PAGE_W - 2 * MARGIN - 3 * GUTTER) / 4
    cards = [
        ("OSM POIs", "2,160", "Commercial and retail points inside baseline 500 m catchments.", PALETTE["pale_teal"]),
        ("Stations", "3", "Gongguan, Zhongxiao Fuxing, and Zhongshan.", PALETTE["pale_green"]),
        ("MRT exits", "15", "Verified station-exit points used for sensitivity testing.", PALETTE["pale_orange"]),
        ("Passenger flow", "1.36M", "March 2026 entries plus exits across the three stations.", colors.HexColor("#eef3fb")),
    ]
    for i, (title, value, note, fill) in enumerate(cards):
        draw_card(c, MARGIN + i * (card_w + GUTTER), card_y, card_w, card_h, title, value, note, fill)

    # Column geometry
    body_top = 14.1 * cm
    col_w = (PAGE_W - 2 * MARGIN - 2 * GUTTER) / 3
    x1 = MARGIN
    x2 = MARGIN + col_w + GUTTER
    x3 = MARGIN + 2 * (col_w + GUTTER)

    frame_body = (
        "<b>Core idea.</b> MRT stations concentrate pedestrian flows and shape nearby commercial environments. "
        "This project compares three different station types using one reproducible spatial workflow.<br/><br/>"
        "<b>Verified metrics.</b> Station coordinates, 500 m buffer distance, EPSG:3826 metric projection, station exits, and March 2026 MRT passenger flow.<br/><br/>"
        "<b>Proxy metrics.</b> OpenStreetMap POI counts, category shares, circular buffers, exit-union buffers, and walk-network catchments."
    )
    draw_box(c, x1, body_top, col_w, 9.0 * cm, "Research Frame", frame_body)

    method_body = (
        "1. Create station points from supplied coordinates.<br/>"
        "2. Project to EPSG:3826 and create 500 m buffers.<br/>"
        "3. Collect OSM POIs and classify retail categories.<br/>"
        "4. Compare circular, exit-based, and walk-network catchments.<br/>"
        "5. Add verified MRT passenger flow as a separate context metric."
    )
    draw_box(c, x1, body_top + 9.7 * cm, col_w, 8.2 * cm, "Method", method_body, fill=colors.HexColor("#fbfdfc"))

    baseline_rows = [["Station", "OSM POIs", "Flow"]]
    for station in ["Zhongshan", "Zhongxiao Fuxing", "Gongguan"]:
        poi = total.loc[total["station_name"] == station, "total_osm_pois"].iloc[0]
        station_flow = flow.loc[flow["station_name"] == station, "total_station_flow"].iloc[0]
        baseline_rows.append([station, fmt_int(poi), fmt_int(station_flow)])
    baseline_table = make_table(baseline_rows, [5.0 * cm, 3.0 * cm, 3.6 * cm], font_size=11.5)
    draw_table_panel(c, x1, body_top + 18.6 * cm, col_w, 6.6 * cm, "Baseline Results", baseline_table)

    data_rows = [
        ["Layer", "Role"],
        ["Station coordinates", "verified input"],
        ["MRT exits", "verified spatial input"],
        ["MRT OD flow", "verified metric"],
        ["OSM POIs", "proxy for retail mix"],
        ["Walk network", "proxy catchment"],
    ]
    data_table = make_table(data_rows, [5.8 * cm, 5.9 * cm], font_size=11.0)
    draw_table_panel(c, x1, body_top + 25.9 * cm, col_w, 7.6 * cm, "Data Status", data_table)

    draw_image_panel(
        c,
        x2,
        body_top,
        col_w,
        16.0 * cm,
        "Observed Retail POIs",
        PROJECT_ROOT / "outputs" / "maps" / "combined_poi_map.png",
        "OSM-based proxy for station-area commercial density.",
    )
    draw_image_panel(
        c,
        x2,
        body_top + 16.7 * cm,
        col_w,
        15.4 * cm,
        "Catchment Sensitivity",
        PROJECT_ROOT / "outputs" / "maps" / "catchment_method_comparison_map.png",
        "Circular, exit-union, and walk-network catchments change the observed footprint.",
    )

    draw_image_panel(
        c,
        x3,
        body_top,
        col_w,
        10.3 * cm,
        "Retail Category Mix",
        PROJECT_ROOT / "outputs" / "charts" / "retail_category_count_by_station.png",
    )
    draw_image_panel(
        c,
        x3,
        body_top + 11.0 * cm,
        col_w,
        8.5 * cm,
        "Passenger Flow",
        PROJECT_ROOT / "outputs" / "charts" / "mrt_passenger_flow_by_station.png",
    )
    draw_image_panel(
        c,
        x3,
        body_top + 20.1 * cm,
        col_w,
        8.6 * cm,
        "POI Count by Catchment Method",
        PROJECT_ROOT / "outputs" / "charts" / "catchment_method_total_poi_comparison.png",
    )

    findings_body = (
        "<b>1. Zhongshan is the largest observed commercial node.</b> It has the highest baseline POI count and the highest verified passenger flow.<br/>"
        "<b>2. Gongguan shows a student-oriented food and cafe profile.</b> High POI density remains visible despite lower station flow.<br/>"
        "<b>3. Zhongxiao Fuxing has high flow but fewer mapped POIs.</b> Premium retail, malls, vertical stores, and underground activity need richer datasets than POI counts.<br/>"
        "<b>4. Catchment choice matters.</b> Exit-based buffers increase counts; walk-network catchments reduce them."
    )
    draw_box(c, x1, body_top + 34.2 * cm, col_w * 2 + GUTTER, 9.5 * cm, "Findings", findings_body, fill=colors.HexColor("#fffdf9"))

    limits_body = (
        "OSM is not an official business register. POI counts do not measure revenue, vacancy, rent, store size, or actual retail visits. "
        "MRT passenger flow measures station entries and exits, not shopping behavior. Business turnover data should only be added after transparent geocoding."
    )
    draw_box(c, x3, body_top + 29.4 * cm, col_w, 8.0 * cm, "Limitations", limits_body, fill=colors.HexColor("#fff8f4"))

    next_body = (
        "Next: validate OSM categories manually, add land-use and building footprints, and extend the same workflow to more MRT stations."
    )
    draw_box(c, x3, body_top + 38.1 * cm, col_w, 5.6 * cm, "Next Step", next_body, fill=colors.HexColor("#f5fbf7"))

    station_y = body_top + 44.4 * cm
    station_profiles = [
        (
            x1,
            "Gongguan: Student Food Node",
            "gongguan",
            "Gongguan",
            "Dense student-oriented food, cafe, health, and everyday-service activity around the MRT station and university area.",
        ),
        (
            x2,
            "Zhongxiao Fuxing: Transfer Node",
            "zhongxiao_fuxing",
            "Zhongxiao Fuxing",
            "High verified passenger flow, but simple POI counts likely understate vertical malls, premium retail, and underground activity.",
        ),
        (
            x3,
            "Zhongshan: Shopping/Culture Node",
            "zhongshan",
            "Zhongshan",
            "Largest observed POI count and highest March 2026 MRT passenger flow among the three station catchments.",
        ),
    ]
    for x, title, station_id, station_name, insight in station_profiles:
        station_total = total.loc[total["station_name"] == station_name, "total_osm_pois"].iloc[0]
        station_flow = flow.loc[flow["station_name"] == station_name, "total_station_flow"].iloc[0]
        count_row = category_counts[category_counts["station_name"] == station_name].iloc[0]
        categories = [col for col in category_counts.columns if col not in {"station_id", "station_name"}]
        top_category = max(categories, key=lambda col: count_row[col])
        stats = [
            ("OSM POIs", fmt_int(station_total)),
            ("MRT flow", fmt_int(station_flow)),
            ("Top category", top_category),
        ]
        if station_id == "gongguan":
            stats[2] = ("Top category", "food")
        draw_station_profile_panel(c, x, station_y, col_w, 13.9 * cm, title, station_map_paths[station_id], stats, insight)

    deliverables_body = (
        "<b>Reproducible GitHub package.</b> 11 Python scripts, one notebook, station points, station exits, circular buffers, exit-based buffers, walk-network catchments, "
        "OSM POI GeoJSON/CSV files, comparison tables, PNG maps/charts, final Markdown report, and this A1 poster generator.<br/>"
        "<b>Why this matters.</b> The project is deliberately transparent: every plotted number can be traced to a source table, and every map can be regenerated from code."
    )
    draw_box(
        c,
        MARGIN,
        body_top + 59.1 * cm,
        PAGE_W - 2 * MARGIN,
        6.5 * cm,
        "Project Deliverables",
        deliverables_body,
        fill=colors.HexColor("#fbfdfc"),
    )

    # Footer
    footer_y = 2.0 * cm
    c.setStrokeColor(PALETTE["line"])
    c.line(MARGIN, footer_y + 0.65 * cm, PAGE_W - MARGIN, footer_y + 0.65 * cm)
    c.setFillColor(PALETTE["muted"])
    c.setFont("Helvetica", 10.5)
    c.drawString(
        MARGIN,
        footer_y,
        "Sources: OpenStreetMap via OSMnx; Taipei Metro OD passenger-flow data; Taipei MRT station-exit coordinate file. Poster size: A1 portrait, 59.4 cm x 84.1 cm.",
    )
    c.drawRightString(PAGE_W - MARGIN, footer_y, GITHUB_URL)

    c.save()


def render_preview():
    import fitz

    doc = fitz.open(POSTER_PDF)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(0.72, 0.72), alpha=False)
    pix.save(POSTER_PREVIEW)


if __name__ == "__main__":
    build_poster()
    render_preview()
    print(f"Saved poster PDF: {POSTER_PDF}")
    print(f"Saved poster preview: {POSTER_PREVIEW}")
