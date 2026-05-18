from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_OUTPUTS = PROJECT_ROOT / "data" / "outputs"
OUTPUTS = PROJECT_ROOT / "outputs"
BUFFERS_DIR = OUTPUTS / "buffers"
CHARTS_DIR = OUTPUTS / "charts"
MAPS_DIR = OUTPUTS / "maps"
TABLES_DIR = OUTPUTS / "tables"
REPORTS_DIR = PROJECT_ROOT / "reports"

WGS84_CRS = "EPSG:4326"
TAIWAN_METRIC_CRS = "EPSG:3826"
BUFFER_METERS = 500
NETWORK_BUFFER_METERS = 500

STATIONS = [
    {
        "station_id": "gongguan",
        "station_name": "Gongguan",
        "lat": 25.0148,
        "lon": 121.5342,
        "node_type": "university/student/food-service node",
    },
    {
        "station_id": "zhongxiao_fuxing",
        "station_name": "Zhongxiao Fuxing",
        "lat": 25.0416,
        "lon": 121.5438,
        "node_type": "high-intensity transfer and premium retail node",
    },
    {
        "station_id": "zhongshan",
        "station_name": "Zhongshan",
        "lat": 25.0526,
        "lon": 121.5204,
        "node_type": "shopping/culture/tourism node",
    },
]

STATION_NAME_ZH = {
    "gongguan": "公館",
    "zhongxiao_fuxing": "忠孝復興",
    "zhongshan": "中山",
}


def ensure_directories() -> None:
    for path in [
        DATA_RAW,
        DATA_PROCESSED,
        DATA_OUTPUTS,
        BUFFERS_DIR,
        CHARTS_DIR,
        MAPS_DIR,
        TABLES_DIR,
        REPORTS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
