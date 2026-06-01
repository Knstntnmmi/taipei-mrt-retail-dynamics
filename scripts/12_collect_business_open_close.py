import io
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests
import urllib3


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"

TAIPEI_ANNUAL_URL = (
    "https://tsis.dbas.gov.taipei/statis/webMain.aspx?"
    "sys=220&ymf=9600&kind=21&type=0&funid=a05011404&cycle=4&outmode=12&compmode=0&outkind=3&deflst=2&nzo=1"
)
GCIS_MONTHLY_INDUSTRY_PAGE = "https://data.gcis.nat.gov.tw/od/detail?oid=DB0B8C8F-9C1A-406F-8760-F7EA18942269"
GCIS_FILE_URL = "https://data.gcis.nat.gov.tw/od/file?oid={oid}"

START_YEAR = 2022

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INDUSTRY_TO_ANALYSIS_CATEGORY = {
    "批發及零售業": "shop/retail",
    "住宿及餐飲業": "food/cafe",
    "其他服務業": "services",
    "支援服務業": "services",
    "藝術、娛樂及休閒服務業": "lifestyle/culture",
    "教育業": "education",
    "醫療保健及社會工作服務業": "health",
    "專業、科學及技術服務業": "professional",
    "出版影音及資通訊業": "information/media",
    "不動產業": "real estate",
    "金融及保險業": "finance",
    "營建工程業": "construction",
    "製造業": "manufacturing",
    "運輸及倉儲業": "transport/storage",
}


def roc_year_to_ad(text: str) -> int:
    match = re.search(r"(\d+)", str(text))
    if not match:
        raise ValueError(f"Cannot parse ROC year from {text!r}")
    return int(match.group(1)) + 1911


def ensure_dirs() -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def fetch_bytes(url: str) -> bytes:
    response = requests.get(url, timeout=45, verify=False)
    response.raise_for_status()
    return response.content


def fetch_text(url: str) -> str:
    response = requests.get(url, timeout=45, verify=False)
    response.raise_for_status()
    return response.text


def clean_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False), errors="coerce").fillna(0).astype(int)


def add_percentages(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    result = df.copy()
    result["open_plus_close"] = result["openings"] + result["closures"]
    if group_cols:
        grouped = result.groupby(group_cols, dropna=False)
        opening_total = grouped["openings"].transform("sum")
        closure_total = grouped["closures"].transform("sum")
    else:
        opening_total = result["openings"].sum()
        closure_total = result["closures"].sum()
    result["opening_share_pct"] = (result["openings"] / opening_total * 100).round(2)
    result["closure_share_pct"] = (result["closures"] / closure_total * 100).round(2)
    result["closure_rate_of_events_pct"] = (
        result["closures"] / result["open_plus_close"].replace(0, pd.NA) * 100
    ).fillna(0).round(2)
    result["net_change"] = result["openings"] - result["closures"]
    return result


def collect_taipei_annual() -> pd.DataFrame:
    df = pd.read_csv(TAIPEI_ANNUAL_URL)
    df.to_csv(DATA_RAW / "taipei_business_registration_by_industry_annual_raw.csv", index=False)

    df = df.rename(
        columns={
            "統計期": "period",
            "行業別": "industry_zh",
            "設立登記家數[家]": "openings",
            "歇業登記家數[家]": "closures",
            "現有家數[家]": "existing_businesses",
        }
    )
    df["year"] = df["period"].apply(roc_year_to_ad)
    for col in ["openings", "closures", "existing_businesses"]:
        df[col] = clean_numeric(df[col])
    df["analysis_category"] = df["industry_zh"].map(INDUSTRY_TO_ANALYSIS_CATEGORY).fillna("other")
    df = df[(df["year"] >= START_YEAR) & (df["industry_zh"] != "總計")].copy()
    return df


def parse_gcis_monthly_links() -> list[tuple[int, int, str]]:
    html = fetch_text(GCIS_MONTHLY_INDUSTRY_PAGE)
    pattern = re.compile(
        r"<td>(\d{4})年(\d{2})月</td>\s*<td[^>]*><a class=\"csv\"\s*"
        r"href=\"javascript: void\(0\)\" onclick=\"javascript:showDialog\('/od/file\?oid=([A-Z0-9-]+)'\)\""
    )
    links = []
    for year, month, oid in pattern.findall(html):
        links.append((int(year), int(month), oid))
    return links


def collect_gcis_monthly_industry() -> pd.DataFrame:
    rows = []
    for year, month, oid in parse_gcis_monthly_links():
        if year < START_YEAR:
            continue
        content = fetch_bytes(GCIS_FILE_URL.format(oid=oid))
        monthly = pd.read_csv(io.BytesIO(content))
        monthly["year"] = year
        monthly["month"] = month
        rows.append(monthly)

    if not rows:
        raise RuntimeError("No GCIS monthly industry files were collected.")

    df = pd.concat(rows, ignore_index=True)
    df.to_csv(DATA_RAW / "gcis_business_registration_industry_monthly_2022_present_raw.csv", index=False)
    df = df.rename(
        columns={
            "行業別": "industry_zh",
            "新設立家數": "openings",
            "歇業家數": "closures",
            "本月底現有家數": "existing_businesses",
        }
    )
    for col in ["openings", "closures", "existing_businesses"]:
        df[col] = clean_numeric(df[col])
    df["analysis_category"] = df["industry_zh"].map(INDUSTRY_TO_ANALYSIS_CATEGORY).fillna("other")
    return df


def aggregate_category_percentages(df: pd.DataFrame, time_cols: list[str]) -> pd.DataFrame:
    grouped = (
        df.groupby(time_cols + ["analysis_category"], dropna=False)[["openings", "closures"]]
        .sum()
        .reset_index()
    )
    return add_percentages(grouped, time_cols)


def save_charts(taipei_category_year: pd.DataFrame, national_category_total: pd.DataFrame) -> None:
    focus_categories = ["shop/retail", "food/cafe", "services", "lifestyle/culture", "education", "health"]

    annual = taipei_category_year[taipei_category_year["analysis_category"].isin(focus_categories)]
    pivot_open = annual.pivot(index="year", columns="analysis_category", values="openings").fillna(0)
    pivot_close = annual.pivot(index="year", columns="analysis_category", values="closures").fillna(0)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharex=True)
    pivot_open.plot(kind="bar", stacked=True, ax=axes[0])
    axes[0].set_title("Taipei Business Openings by Category")
    axes[0].set_ylabel("Business registrations")
    axes[0].set_xlabel("")
    pivot_close.plot(kind="bar", stacked=True, ax=axes[1])
    axes[1].set_title("Taipei Business Closures by Category")
    axes[1].set_ylabel("Business closures")
    axes[1].set_xlabel("")
    for ax in axes:
        ax.tick_params(axis="x", rotation=0)
        ax.legend(title="Category", fontsize=8)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "taipei_business_open_close_by_category_2022_2025.png", dpi=200)
    plt.close(fig)

    national_focus = national_category_total[national_category_total["analysis_category"].isin(focus_categories)].copy()
    national_focus = national_focus.sort_values("closure_rate_of_events_pct", ascending=False)
    x = range(len(national_focus))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, national_focus["opening_share_pct"], label="Opening share %", color="#2d8a62")
    ax.bar(x, -national_focus["closure_share_pct"], label="Closure share %", color="#d66a2f")
    ax.axhline(0, color="#172026", linewidth=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(national_focus["analysis_category"], rotation=25, ha="right")
    ax.set_ylabel("Share of all openings / closures (%)")
    ax.set_title("2022-present Business Opening/Closing Shares by Category")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "business_open_close_percentage_shares_2022_present.png", dpi=200)
    plt.close(fig)


def main() -> None:
    ensure_dirs()

    taipei_annual = collect_taipei_annual()
    taipei_annual.to_csv(TABLES_DIR / "taipei_business_open_close_by_industry_2022_2025.csv", index=False)
    taipei_category_year = aggregate_category_percentages(taipei_annual, ["year"])
    taipei_category_year.to_csv(TABLES_DIR / "taipei_business_open_close_percentages_by_category_2022_2025.csv", index=False)
    taipei_category_total = aggregate_category_percentages(taipei_annual, [])
    taipei_category_total.to_csv(TABLES_DIR / "taipei_business_open_close_category_totals_2022_2025.csv", index=False)

    monthly = collect_gcis_monthly_industry()
    monthly.to_csv(TABLES_DIR / "gcis_business_open_close_by_industry_monthly_2022_present.csv", index=False)
    national_category_total = aggregate_category_percentages(monthly, [])
    national_category_total.to_csv(TABLES_DIR / "gcis_business_open_close_category_totals_2022_present.csv", index=False)
    national_category_month = aggregate_category_percentages(monthly, ["year", "month"])
    national_category_month.to_csv(TABLES_DIR / "gcis_business_open_close_percentages_monthly_2022_present.csv", index=False)

    save_charts(taipei_category_year, national_category_total)

    latest_year = int(monthly["year"].max())
    latest_month = int(monthly.loc[monthly["year"] == latest_year, "month"].max())
    summary = pd.DataFrame(
        [
            {
                "metric": "taipei_annual_industry_years",
                "value": f"{int(taipei_annual['year'].min())}-{int(taipei_annual['year'].max())}",
            },
            {
                "metric": "gcis_monthly_industry_period",
                "value": f"{int(monthly['year'].min())}-01 to {latest_year}-{latest_month:02d}",
            },
            {"metric": "gcis_monthly_records", "value": str(len(monthly))},
            {"metric": "source_note", "value": "Taipei annual data is city-level; GCIS monthly industry data is national-level."},
        ]
    )
    summary.to_csv(TABLES_DIR / "business_open_close_data_status.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
