"""One-time script: download a year of weather and save one CSV per city.

Data comes from Open-Meteo's free historical archive (no API key needed).
The web app never goes online; it only reads the CSVs this script writes.

Run from the weather-webapp folder:
    python fetch_data.py
"""

import csv
from datetime import date, datetime

import requests

from weather_data import (
    DATA_DIR, FIRST_DATE, LAST_DATE,
    HI_LO_SEPARATOR, HOURLY_SEPARATOR, SUN_SEPARATOR,
    city_to_filename,
)

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# city name -> (latitude, longitude)
CITIES = {
    "Chicago": (41.8781, -87.6298),
    "Philadelphia": (39.9526, -75.1652),
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "London": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "Tokyo": (35.6762, 139.6503),
    "Sydney": (-33.8688, 151.2093),
}

# Open-Meteo describes the weather with a number (WMO weather code).
WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Freezing fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    56: "Light freezing drizzle", 57: "Freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Freezing rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Light rain showers", 81: "Rain showers", 82: "Violent rain showers",
    85: "Light snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail",
    99: "Severe thunderstorm with hail",
}


def describe_weather_code(code):
    if code is None:
        return ""
    return WEATHER_CODES.get(code, "Unknown")


def format_temp(value):
    return "" if value is None else f"{value:.1f}"


def format_time(iso_text):
    """'2025-11-10T06:32' -> '06:32 AM'"""
    if not iso_text:
        return ""
    return datetime.fromisoformat(iso_text).strftime("%I:%M %p")


def build_rows(api_json):
    """Turn Open-Meteo's JSON answer into the 5 CSV rows (one column per day)."""
    daily = api_json["daily"]
    hourly = api_json["hourly"]

    # Group hourly temps by day: '2025-11-10T05:00'[:10] -> '2025-11-10'
    temps_by_day = {}
    for time_text, temp in zip(hourly["time"], hourly["temperature_2m"]):
        temps_by_day.setdefault(time_text[:10], []).append(temp)

    dates, hi_lo, hourly_cells, conditions, sun = [], [], [], [], []
    for i, iso_day in enumerate(daily["time"]):
        dates.append(date.fromisoformat(iso_day).strftime("%m/%d/%Y"))
        hi_lo.append(
            format_temp(daily["temperature_2m_max"][i])
            + HI_LO_SEPARATOR
            + format_temp(daily["temperature_2m_min"][i])
        )
        hourly_cells.append(
            HOURLY_SEPARATOR.join(format_temp(t) for t in temps_by_day.get(iso_day, []))
        )
        conditions.append(describe_weather_code(daily["weather_code"][i]))
        sun.append(
            format_time(daily["sunset"][i]) + SUN_SEPARATOR + format_time(daily["sunrise"][i])
        )
    return [dates, hi_lo, hourly_cells, conditions, sun]


def download(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": FIRST_DATE.isoformat(),
        "end_date": LAST_DATE.isoformat(),
        "daily": "temperature_2m_max,temperature_2m_min,weather_code,sunrise,sunset",
        "hourly": "temperature_2m",
        "temperature_unit": "fahrenheit",
        "timezone": "auto",  # report times in the city's own local time
    }
    response = requests.get(ARCHIVE_URL, params=params, timeout=60)
    response.raise_for_status()  # stop with an error if the download failed
    return response.json()


def main():
    DATA_DIR.mkdir(exist_ok=True)
    for city, (lat, lon) in CITIES.items():
        print(f"Downloading {city}...")
        rows = build_rows(download(lat, lon))
        path = DATA_DIR / city_to_filename(city)
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
        print(f"  saved {len(rows[0])} days to {path.name}")


if __name__ == "__main__":
    main()
