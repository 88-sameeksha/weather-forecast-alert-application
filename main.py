"""Command-line entry point for the Weather Forecast & Alert Application."""
import argparse
import os
from dotenv import load_dotenv

from src.weather_service import fetch_live_weather
from src.simulation import load_sample_weather
from src.processor import build_forecast_dataframe, build_current_summary
from src.alerts import generate_alerts
from src.reports import save_reports
from src.visualization import create_weather_chart


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Weather Forecast & Alert Application")
    parser.add_argument("--mode", choices=["simulation", "api"], default="simulation",
                        help="Use local sample data or the live OpenWeatherMap API")
    parser.add_argument("--city", default=None, help="City name (example: Kanpur)")
    parser.add_argument("--temp-limit", type=float, default=38.0,
                        help="High-temperature alert threshold in Celsius")
    parser.add_argument("--humidity-limit", type=float, default=85.0,
                        help="High-humidity alert threshold in percent")
    parser.add_argument("--rain-limit", type=float, default=60.0,
                        help="Rain-probability alert threshold in percent")
    args = parser.parse_args()

    city = args.city or input("Enter city name: ").strip()
    if not city:
        raise SystemExit("City name cannot be empty.")

    thresholds = {
        "temperature_c": args.temp_limit,
        "humidity_percent": args.humidity_limit,
        "rain_probability_percent": args.rain_limit,
    }

    try:
        if args.mode == "simulation":
            current, forecast = load_sample_weather(city)
            print("\nMODE: SIMULATION (sample data; not live weather)")
        else:
            api_key = os.getenv("OPENWEATHER_API_KEY")
            if not api_key:
                raise ValueError("OPENWEATHER_API_KEY is missing. Add it to your .env file.")
            current, forecast = fetch_live_weather(city, api_key)
            print("\nMODE: LIVE API")

        summary = build_current_summary(current)
        forecast_df = build_forecast_dataframe(forecast)
        alerts = generate_alerts(summary, forecast_df, thresholds)

        print("\n" + "=" * 58)
        print(f"WEATHER REPORT: {summary['city']}, {summary['country']}")
        print("=" * 58)
        print(f"Condition       : {summary['condition']}")
        print(f"Temperature     : {summary['temperature_c']:.1f} °C")
        print(f"Feels like      : {summary['feels_like_c']:.1f} °C")
        print(f"Humidity        : {summary['humidity_percent']}%")
        print(f"Wind speed      : {summary['wind_speed_mps']:.1f} m/s")
        print(f"Cloud cover     : {summary['cloud_percent']}%")
        print(f"Observation time: {summary['observed_at']}")

        print("\nFORECAST (next available intervals)")
        print("-" * 58)
        print(forecast_df.head(10).to_string(index=False))

        print("\nALERTS")
        print("-" * 58)
        if alerts:
            for item in alerts:
                print(f"[{item['severity']}] {item['type']}: {item['message']}")
        else:
            print("No configured alert thresholds were exceeded.")

        paths = save_reports(summary, forecast_df, alerts, thresholds)
        chart_path = create_weather_chart(forecast_df, summary["city"])
        print("\nFILES CREATED")
        for label, path in {**paths, "chart": chart_path}.items():
            print(f"{label}: {path}")

    except (ValueError, RuntimeError) as exc:
        print(f"\nApplication error: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
