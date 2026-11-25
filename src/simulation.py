"""Load deterministic local sample data for offline demonstrations."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sample_weather.json"


def load_sample_weather(city):
    with DATA_FILE.open("r", encoding="utf-8") as file:
        sample = json.load(file)

    # Keep the sample readings but let the user demonstrate another city label.
    current = sample["current"].copy()
    current["name"] = city
    forecast = sample["forecast"].copy()
    forecast["city"] = {**forecast.get("city", {}), "name": city}
    return current, forecast
