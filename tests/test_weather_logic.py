"""Tests for the program's logic (no web pages, no internet).

Run from the weather-webapp folder:  python -m pytest
"""

import csv
from datetime import date

import pytest

import weather_data as wd
from fetch_data import build_rows, describe_weather_code, format_time


def fake_api_json():
    """A tiny, made-up answer shaped like Open-Meteo's real one (2 days)."""
    days = ["2025-11-10", "2025-11-11"]
    return {
        "daily": {
            "time": days,
            "temperature_2m_max": [52.34, 60.0],
            "temperature_2m_min": [38.1, None],
            "weather_code": [61, 0],
            "sunrise": ["2025-11-10T06:32", "2025-11-11T06:33"],
            "sunset": ["2025-11-10T16:31", "2025-11-11T16:30"],
        },
        "hourly": {
            "time": [f"{d}T{h:02d}:00" for d in days for h in range(24)],
            "temperature_2m": [float(h) for h in range(48)],
        },
    }


@pytest.fixture
def data_dir(tmp_path):
    """Write a fake chicago.csv into a temporary folder."""
    rows = build_rows(fake_api_json())
    with open(tmp_path / "chicago.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    return tmp_path


# ---- fetch_data: turning API data into CSV rows ----

def test_build_rows_layout():
    dates, hi_lo, hourly, conditions, sun = build_rows(fake_api_json())
    assert dates == ["11/10/2025", "11/11/2025"]
    assert hi_lo == ["52.3/38.1", "60.0/"]          # missing low -> empty
    assert len(hourly[0].split(";")) == 24
    assert hourly[1].split(";")[0] == "24.0"         # day 2 starts at hour 24
    assert conditions == ["Light rain", "Clear sky"]
    assert sun[0] == "04:31 PM;06:32 AM"             # spec order: sunset, sunrise


def test_describe_weather_code():
    assert describe_weather_code(95) == "Thunderstorm"
    assert describe_weather_code(12345) == "Unknown"
    assert describe_weather_code(None) == ""


def test_format_time():
    assert format_time("2025-11-10T16:31") == "04:31 PM"
    assert format_time(None) == ""


# ---- weather_data: reading CSVs and checking input ----

def test_city_filename_round_trip():
    assert wd.city_to_filename(" New York ") == "new_york.csv"
    assert wd.filename_to_city("new_york.csv") == "New York"


def test_parse_date_accepts_both_formats():
    assert wd.parse_date("2025-11-10") == date(2025, 11, 10)
    assert wd.parse_date("11/10/2025") == date(2025, 11, 10)


@pytest.mark.parametrize("text", ["11/09/2025", "11/11/2026", "hello", ""])
def test_parse_date_rejects_bad_or_out_of_range(text):
    with pytest.raises(wd.WeatherError):
        wd.parse_date(text)


def test_hour_label():
    assert [wd.hour_label(h) for h in (0, 1, 12, 23)] == ["12 AM", "1 AM", "12 PM", "11 PM"]


def test_lookup_finds_the_right_day(data_dir):
    w = wd.lookup("chicago", "2025-11-10", data_dir)    # lowercase works too
    assert w["city"] == "Chicago"
    assert w["date"] == "Monday, November 10, 2025"
    assert (w["high"], w["low"]) == (52.3, 38.1)
    assert w["conditions"] == "Light rain"
    assert (w["sunrise"], w["sunset"]) == ("06:32 AM", "04:31 PM")
    assert w["hourly"][0] == {"hour": "12 AM", "temp": 0.0}
    assert len(w["hourly"]) == 24


def test_lookup_handles_missing_value(data_dir):
    w = wd.lookup("Chicago", "11/11/2025", data_dir)
    assert w["low"] is None


def test_lookup_unknown_city(data_dir):
    with pytest.raises(wd.WeatherError, match="Available cities: Chicago"):
        wd.lookup("Atlantis", "2025-11-10", data_dir)


def test_lookup_date_not_in_file(data_dir):
    with pytest.raises(wd.WeatherError, match="No data for Chicago"):
        wd.lookup("Chicago", "2025-12-25", data_dir)


def test_lookup_requires_both_fields(data_dir):
    with pytest.raises(wd.WeatherError, match="both"):
        wd.lookup("", "2025-11-10", data_dir)
