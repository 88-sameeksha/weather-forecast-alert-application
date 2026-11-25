"""Rule-based weather alerts. Thresholds are configurable by the user."""


def generate_alerts(current, forecast_df, thresholds):
    alerts = []

    if current["temperature_c"] >= thresholds["temperature_c"]:
        alerts.append({
            "type": "High temperature",
            "severity": "WARNING",
            "message": (
                f"Current temperature is {current['temperature_c']:.1f} °C, "
                f"at or above the configured {thresholds['temperature_c']:.1f} °C threshold."
            ),
        })

    if current["humidity_percent"] >= thresholds["humidity_percent"]:
        alerts.append({
            "type": "High humidity",
            "severity": "INFO",
            "message": (
                f"Current humidity is {current['humidity_percent']}%, "
                f"at or above the configured {thresholds['humidity_percent']:.0f}% threshold."
            ),
        })

    if not forecast_df.empty:
        max_pop = float(forecast_df["rain_probability_percent"].max())
        max_rain = float(forecast_df["rain_3h_mm"].max())
        if max_pop >= thresholds["rain_probability_percent"] or max_rain > 0:
            alerts.append({
                "type": "Rain forecast",
                "severity": "WARNING" if max_pop >= thresholds["rain_probability_percent"] else "INFO",
                "message": (
                    f"Forecast rain probability peaks at {max_pop:.0f}%; "
                    f"maximum forecast 3-hour rainfall is {max_rain:.1f} mm."
                ),
            })

        storm_rows = forecast_df[
            forecast_df["main_condition"].str.lower().str.contains("thunderstorm", na=False)
        ]
        if not storm_rows.empty:
            alerts.append({
                "type": "Thunderstorm condition",
                "severity": "WARNING",
                "message": "A thunderstorm condition appears in the forecast. Check official local updates.",
            })

    return alerts
