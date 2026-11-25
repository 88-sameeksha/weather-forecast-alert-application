"""Save machine-readable JSON and tabular CSV reports."""
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"


def save_reports(current, forecast_df, alerts, thresholds):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    city_slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in current["city"]).strip("_")

    csv_path = OUTPUT_DIR / f"{city_slug}_forecast_{stamp}.csv"
    json_path = OUTPUT_DIR / f"{city_slug}_weather_report_{stamp}.json"
    alerts_path = OUTPUT_DIR / f"{city_slug}_alerts_{stamp}.csv"

    forecast_df.to_csv(csv_path, index=False)

    report = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "current_weather": current,
        "thresholds": thresholds,
        "alerts": alerts,
        "forecast_records": forecast_df.to_dict(orient="records"),
    }
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    pd.DataFrame(alerts, columns=["type", "severity", "message"]).to_csv(alerts_path, index=False)

    return {"forecast_csv": str(csv_path), "weather_json": str(json_path), "alerts_csv": str(alerts_path)}
