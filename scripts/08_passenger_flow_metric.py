from pathlib import Path

import pandas as pd

from project_config import DATA_RAW, STATION_NAME_ZH, TABLES_DIR, ensure_directories


SOURCE_OD = Path("/Users/konstantin/Documents/Playground/retail_vacancy_prediction/data/raw/mrt_od_latest.csv")


def main() -> None:
    ensure_directories()
    if not SOURCE_OD.exists():
        raise FileNotFoundError(f"Missing source MRT OD file: {SOURCE_OD}")

    od = pd.read_csv(SOURCE_OD)
    station_rows = []
    for station_id, zh_name in STATION_NAME_ZH.items():
        entries = od.loc[od["進站"] == zh_name, "人次"].sum()
        exits = od.loc[od["出站"] == zh_name, "人次"].sum()
        station_rows.append(
            {
                "station_id": station_id,
                "station_name": {
                    "gongguan": "Gongguan",
                    "zhongxiao_fuxing": "Zhongxiao Fuxing",
                    "zhongshan": "Zhongshan",
                }[station_id],
                "station_name_zh": zh_name,
                "month": str(od["日期"].min())[:7],
                "verified_metric": "Taipei Metro OD passenger flow",
                "entries": int(entries),
                "exits": int(exits),
                "total_station_flow": int(entries + exits),
                "source_file": str(SOURCE_OD),
            }
        )

    flow = pd.DataFrame(station_rows).sort_values("total_station_flow", ascending=False)
    flow.to_csv(TABLES_DIR / "mrt_passenger_flow_by_station.csv", index=False)
    flow.to_csv(DATA_RAW / "mrt_passenger_flow_by_station.csv", index=False)
    print("Saved MRT passenger-flow comparison table.")


if __name__ == "__main__":
    main()
