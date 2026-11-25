"""Live OpenWeatherMap API integration using geocoding and coordinates."""
import requests

BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"


def _get_json(url, params):
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 401:
            raise RuntimeError("API key is invalid or not yet activated (HTTP 401).")
        if response.status_code == 404:
            raise RuntimeError("Location not found. Check the city spelling.")
        if response.status_code == 429:
            raise RuntimeError("API rate limit reached. Try again later.")
        response.raise_for_status()
        return response.json()
    except requests.Timeout as exc:
        raise RuntimeError("Weather API request timed out. Check your connection.") from exc
    except requests.ConnectionError as exc:
        raise RuntimeError("Could not connect to the weather service.") from exc
    except requests.HTTPError as exc:
        raise RuntimeError(f"Weather API returned an HTTP error: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("Weather API returned invalid JSON.") from exc


def fetch_live_weather(city, api_key):
    """Fetch current conditions and a 5-day/3-hour forecast for a city."""
    locations = _get_json(GEO_URL, {"q": city, "limit": 1, "appid": api_key})
    if not locations:
        raise RuntimeError("City not found. Try a more specific city name.")

    location = locations[0]
    coordinates = {"lat": location["lat"], "lon": location["lon"],
                   "appid": api_key, "units": "metric"}
    current = _get_json(f"{BASE_URL}/weather", coordinates)
    forecast = _get_json(f"{BASE_URL}/forecast", coordinates)
    if "list" not in forecast:
        raise RuntimeError("Forecast response did not contain a forecast list.")
    return current, forecast
