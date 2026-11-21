# Project Notes

- Default mode is offline simulation.
- Live mode resolves a city through OpenWeatherMap Geocoding, then calls Current Weather and 5 Day / 3 Hour Forecast endpoints using coordinates.
- The forecast endpoint returns 3-hour intervals; it is not a daily forecast endpoint.
- Alert thresholds are configurable through command-line arguments or the optional Streamlit sidebar.
- Alerts are rule-based educational notifications, not official severe-weather warnings.
