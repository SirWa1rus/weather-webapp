"""Reading weather out of the per-city CSV files.

This module is the "logic" of the app. It knows nothing about web pages:
app.py calls lookup() and gets back a plain dictionary to display.

CSV layout (one file per city, e.g. data/chicago.csv). Each ROW is one kind of
information and each COLUMN is one day, so column n of every row is the same day:

    row 1: date                 e.g. 11/10/2025
    row 2: high/low (F)         e.g. 52.3/38.1
    row 3: 24 hourly temps (F)  e.g. 40.1;39.8;...   (separated by ';')
    row 4: conditions           e.g. Light rain
    row 5: sunset;sunrise       e.g. 04:31 PM;06:32 AM

A missing value is stored as an empty string.
"""

import csv
from datetime import date, datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
FIRST_DATE = date(2025, 11, 10)
LAST_DATE = date(2026, 11, 10)

HOURLY_SEPARATOR = ";"
HI_LO_SEPARATOR = "/"
SUN_SEPARATOR = ";"

# Which row holds what (0-based, because Python lists start at 0).
ROW_DATE, ROW_HI_LO, ROW_HOURLY, ROW_CONDITIONS, ROW_SUN = range(5)


class WeatherError(Exception):
    """A problem we can explain to the user (bad city, bad date, ...)."""


def city_to_filename(city):
    """'New York' -> 'new_york.csv'"""
    return city.strip().lower().replace(" ", "_") + ".csv"


def filename_to_city(filename):
    """'new_york.csv' -> 'New York'"""
    return Path(filename).stem.replace("_", " ").title()


def available_cities(data_dir=DATA_DIR):
    """Names of every city that has a CSV file, sorted A-Z."""
    return sorted(filename_to_city(p.name) for p in Path(data_dir).glob("*.csv"))


def parse_date(text):
    """Turn user text into a date and make sure it is in the supported range.

    Accepts YYYY-MM-DD (what a browser date picker sends) or MM/DD/YYYY.
    """
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            day = datetime.strptime(text, fmt).date()
            break
        except ValueError:
            continue
    else:  # runs only if the loop never hit 'break'
        raise WeatherError(f"'{text}' is not a date. Use MM/DD/YYYY.")

    if not FIRST_DATE <= day <= LAST_DATE:
        raise WeatherError(
            f"Pick a date from {FIRST_DATE:%B %d, %Y} to {LAST_DATE:%B %d, %Y}."
        )
    return day


def to_number(text):
    """'52.3' -> 52.3, '' -> None (missing)."""
    return float(text) if text.strip() else None


def parse_hi_lo(cell):
    """'52.3/38.1' -> (52.3, 38.1)"""
    high, low = cell.split(HI_LO_SEPARATOR)
    return to_number(high), to_number(low)


def hour_label(hour):
    """0 -> '12 AM', 13 -> '1 PM'"""
    suffix = "AM" if hour < 12 else "PM"
    return f"{hour % 12 or 12} {suffix}"


def parse_hourly(cell):
    """'40.1;39.8;...' -> [{'hour': '12 AM', 'temp': 40.1}, ...]"""
    temps = [to_number(t) for t in cell.split(HOURLY_SEPARATOR)]
    return [{"hour": hour_label(i), "temp": t} for i, t in enumerate(temps)]


def parse_sun(cell):
    """'04:31 PM;06:32 AM' -> ('06:32 AM', '04:31 PM')  i.e. (sunrise, sunset)"""
    sunset, sunrise = cell.split(SUN_SEPARATOR)
    return sunrise or None, sunset or None


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def get_day_weather(city, day, data_dir=DATA_DIR):
    """Find one day's weather for a city. Returns a dictionary."""
    path = Path(data_dir) / city_to_filename(city)
    if not path.exists():
        choices = ", ".join(available_cities(data_dir)) or "none yet"
        raise WeatherError(f"No data for '{city}'. Available cities: {choices}.")

    rows = read_rows(path)
    wanted = day.strftime("%m/%d/%Y")
    if wanted not in rows[ROW_DATE]:
        raise WeatherError(f"No data for {city} on {wanted}.")
    col = rows[ROW_DATE].index(wanted)

    high, low = parse_hi_lo(rows[ROW_HI_LO][col])
    sunrise, sunset = parse_sun(rows[ROW_SUN][col])
    return {
        "city": filename_to_city(path.name),
        "date": f"{day:%A, %B} {day.day}, {day.year}",
        "high": high,
        "low": low,
        "hourly": parse_hourly(rows[ROW_HOURLY][col]),
        "conditions": rows[ROW_CONDITIONS][col] or None,
        "sunrise": sunrise,
        "sunset": sunset,
    }


def lookup(city, date_text, data_dir=DATA_DIR):
    """Check the user's raw input, then return that day's weather."""
    if not city.strip() or not date_text.strip():
        raise WeatherError("Enter both a location and a date.")
    return get_day_weather(city, parse_date(date_text), data_dir)
