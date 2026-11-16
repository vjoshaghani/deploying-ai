from datetime import date, datetime
from zoneinfo import ZoneInfo

import requests


def get_ottawa_weather(visit_date: str) -> dict:
    """Get Ottawa's forecast for a date formatted as YYYY-MM-DD."""
    try:
        requested_date = date.fromisoformat(visit_date)
    except ValueError:
        return {
            "available": False,
            "reason": "Use a date formatted as YYYY-MM-DD.",
        }

    today = datetime.now(ZoneInfo("America/Toronto")).date()
    days_ahead = (requested_date - today).days

    if not 0 <= days_ahead <= 6:
        return {
            "available": False,
            "reason": "Forecasts support today through six days ahead.",
        }

    parameters = {
        "latitude": 45.4215,
        "longitude": -75.6972,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max"
        ),
        "temperature_unit": "celsius",
        "timezone": "America/Toronto",
        "forecast_days": 7,
    }

    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params=parameters,
            timeout=15,
        )
        response.raise_for_status()
        daily = response.json()["daily"]

        index = daily["time"].index(visit_date)

        high = daily["temperature_2m_max"][index]
        low = daily["temperature_2m_min"][index]
        precipitation = daily["precipitation_probability_max"][index]

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        IndexError,
        TypeError,
    ):
        return {
            "available": False,
            "reason": "The weather service could not provide a forecast.",
        }

    if any(value is None for value in [high, low, precipitation]):
        return {
            "available": False,
            "reason": "The forecast contains missing weather values.",
        }

    return {
        "available": True,
        "location": "Ottawa",
        "date": visit_date,
        "temperature_high_c": high,
        "temperature_low_c": low,
        "precipitation_probability_max_percent": precipitation,
        "source": "Open-Meteo",
        "source_url": "https://open-meteo.com/",
    }