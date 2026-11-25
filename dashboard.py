"""Optional Streamlit dashboard. Install requirements-dashboard.txt first."""
import os
import streamlit as st
from dotenv import load_dotenv

from src.weather_service import fetch_live_weather
from src.simulation import load_sample_weather
from src.processor import build_current_summary, build_forecast_dataframe
from src.alerts import generate_alerts
from src.reports import save_reports
from src.visualization import create_weather_chart

load_dotenv()
st.set_page_config(page_title="Weather Forecast & Alerts", page_icon="🌦️", layout="wide")
st.title("🌦️ Weather Forecast & Alert Application")
st.caption("Educational project — simulation data is not live weather or an official warning service.")

with st.sidebar:
    city = st.text_input("City", value="Kanpur")
    mode = st.radio("Data source", ["Simulation", "Live API"])
    temp_limit = st.number_input("High temperature threshold (°C)", value=38.0)
    humidity_limit = st.number_input("High humidity threshold (%)", value=85.0, min_value=0.0, max_value=100.0)
    rain_limit = st.number_input("Rain probability threshold (%)", value=60.0, min_value=0.0, max_value=100.0)
    run = st.button("Get weather", type="primary")

if run:
    try:
        if mode == "Simulation":
            current, raw_forecast = load_sample_weather(city)
            st.info("Simulation mode: these are fictional sample readings.")
        else:
            key = os.getenv("OPENWEATHER_API_KEY")
            if not key:
                st.error("Add OPENWEATHER_API_KEY to your .env file.")
                st.stop()
            current, raw_forecast = fetch_live_weather(city, key)

        summary = build_current_summary(current)
        forecast = build_forecast_dataframe(raw_forecast)
        thresholds = {"temperature_c": temp_limit, "humidity_percent": humidity_limit,
                      "rain_probability_percent": rain_limit}
        alerts = generate_alerts(summary, forecast, thresholds)

        st.subheader(f"Current weather — {summary['city']}, {summary['country']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Temperature", f"{summary['temperature_c']:.1f} °C")
        c2.metric("Feels like", f"{summary['feels_like_c']:.1f} °C")
        c3.metric("Humidity", f"{summary['humidity_percent']}%")
        c4.metric("Wind", f"{summary['wind_speed_mps']:.1f} m/s")

        st.subheader("Forecast")
        st.dataframe(forecast, use_container_width=True)
        st.subheader("Alerts")
        if alerts:
            for alert in alerts:
                st.warning(f"{alert['severity']} — {alert['type']}: {alert['message']}")
        else:
            st.success("No configured alert thresholds were exceeded.")

        csv_bytes = forecast.to_csv(index=False).encode("utf-8")
        st.download_button("Download forecast CSV", csv_bytes, file_name="weather_forecast.csv", mime="text/csv")
        paths = save_reports(summary, forecast, alerts, thresholds)
        chart = create_weather_chart(forecast, summary["city"])
        st.image(chart, caption="Forecast temperature and rain probability")
        st.caption("Saved local report: " + paths["weather_json"])
    except (ValueError, RuntimeError, KeyError) as exc:
        st.error(str(exc))
