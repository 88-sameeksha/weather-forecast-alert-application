"""Convert API JSON into simple Python dictionaries and a Pandas DataFrame."""
from datetime import datetime, timezone
import pandas as pd


def _local_time(unix_timestamp, timezone_offset=0):
    # OpenWeatherMap timestamps are UTC Unix timestamps. Apply city offset.
    dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    from datetime import timedelta
    return (dt + timedelta(seconds=timezone_offset)).strftime("%Y-%m-%d %H:%M")


def build_current_summary(data):
    weather = (data.get("weather") or [{}])[0]
    main = data.get("main", {})
    wind = data.get("wind", {})
    return {
        "city": data.get("name", "Unknown"),
        "country": data.get("sys", {}).get("country", ""),
        "condition": weather.get("description", "Unknown").title(),
        "main_condition": weather.get("main", "Unknown"),
        "temperature_c": float(main.get("temp", 0)),
        "feels_like_c": float(main.get("feels_like", main.get("temp", 0))),
        "humidity_percent": int(main.get("humidity", 0)),
        "wind_speed_mps": float(wind.get("speed", 0)),
        "cloud_percent": int(data.get("clouds", {}).get("all", 0)),
        "observed_at": _local_time(data.get("dt", 0), data.get("timezone", 0)),
    }


def build_forecast_dataframe(data):
    rows = []
    city_offset = data.get("city", {}).get("timezone", 0)
    for item in data.get("list", []):
        weather = (item.get("weather") or [{}])[0]
        main = item.get("main", {})
        rain = item.get("rain", {}).get("3h", 0.0)
        pop = float(item.get("pop", 0.0)) * 100
        rows.append({
            "forecast_time": _local_time(item.get("dt", 0), city_offset),
            "temperature_c": float(main.get("temp", 0)),
            "feels_like_c": float(main.get("feels_like", main.get("temp", 0))),
            "humidity_percent": int(main.get("humidity", 0)),
            "rain_probability_percent": round(pop, 1),
            "rain_3h_mm": float(rain),
            "wind_speed_mps": float(item.get("wind", {}).get("speed", 0)),
            "condition": weather.get("description", "Unknown").title(),
            "main_condition": weather.get("main", "Unknown"),
        })

    columns = [
        "forecast_time", "temperature_c", "feels_like_c", "humidity_percent",
        "rain_probability_percent", "rain_3h_mm", "wind_speed_mps",
        "condition", "main_condition"
    ]
    return pd.DataFrame(rows, columns=columns)
