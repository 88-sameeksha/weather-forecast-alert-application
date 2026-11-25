"""Create a forecast temperature and rain-probability chart."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Works on machines without a graphical display.
import matplotlib.pyplot as plt

IMAGE_DIR = Path(__file__).resolve().parents[1] / "images"


def create_weather_chart(forecast_df, city):
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    safe_city = "".join(ch.lower() if ch.isalnum() else "_" for ch in city).strip("_")
    output_path = IMAGE_DIR / f"{safe_city}_forecast_chart.png"

    if forecast_df.empty:
        raise ValueError("Cannot create a chart because the forecast is empty.")

    x = range(len(forecast_df))
    labels = forecast_df["forecast_time"].tolist()

    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(x, forecast_df["temperature_c"], marker="o", label="Temperature (°C)")
    ax1.set_xlabel("Forecast interval")
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_xticks(list(x)[::max(1, len(x) // 8)])
    ax1.set_xticklabels(labels[::max(1, len(labels) // 8)], rotation=35, ha="right")
    ax1.grid(True, alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(x, forecast_df["rain_probability_percent"], marker="s",
             linestyle="--", label="Rain probability (%)")
    ax2.set_ylabel("Rain probability (%)")
    ax2.set_ylim(0, 100)

    fig.suptitle(f"Weather Forecast – {city}")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return str(output_path)
