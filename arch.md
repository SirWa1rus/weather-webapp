# Architecture (handoff for other agents)

Read `spec.md` for what the program does. Do not read `problem.md`.

## Overview

A Python web app (FastAPI) where the user enters a city and a date
(11/10/2025 to 11/10/2026) and sees that day's weather. All data is read from
local CSV files; the app never goes online at runtime.

## Files

| File                          | Role                                                                                                                                                                                                                       |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fetch_data.py`               | One-time script. Downloads a year of weather per city from the Open-Meteo archive API (free, no key) and writes `data/<city>.csv`. City list + coordinates live in `CITIES`. `build_rows()` converts API JSON to CSV rows. |
| `weather_data.py`             | Core logic, no web code. Reads CSVs, validates input (`parse_date`), returns one day as a dict (`lookup`, `get_day_weather`). Raises `WeatherError` for user-facing problems.                                              |
| `app.py`                      | FastAPI app. One route `GET /` with query params `city` and `date`; renders `templates/index.html`. Run with `python app.py` (uvicorn on port 8000).                                                                       |
| `templates/index.html`        | Jinja2 template: rounded search bar + rounded info cards.                                                                                                                                                                  |
| `static/style.css`            | Dark gray background (#2b2b2b), cards with 16px radius, pill search bar.                                                                                                                                                   |
| `tests/test_weather_logic.py` | pytest tests for logic only (fetch_data.build_rows + weather_data). No network, uses a temp folder. Run `python -m pytest`.                                                                                                |
| `requirements.txt`            | fastapi, uvicorn, jinja2, requests, pytest                                                                                                                                                                                 |

## CSV format (`data/<city>.csv`, file name = lowercase city, spaces -> `_`)

Each row is one field; each column is one day (column n is the same day in every row).

1. date `MM/DD/YYYY`
2. `high/low` in °F, e.g. `52.3/38.1`
3. 24 hourly temps in °F separated by `;` (local time)
4. conditions text (from WMO weather code), e.g. `Light rain`
5. `sunset;sunrise`, e.g. `04:31 PM;06:32 AM` (spec order: sunset first)

Missing values are empty strings; the UI shows `—`.

## Decisions

- Data: Open-Meteo archive, downloaded once (no API key).
- Locations: fixed list of 8 cities. Add a city by adding it to `CITIES` and rerunning `fetch_data.py`.
- Natural disasters: excluded entirely (user decision).
- HTTPS: plain http for local development for now.
- Framework: FastAPI (user switched from Flask).

## Ideas for later

- nothing yet (user will decide)
