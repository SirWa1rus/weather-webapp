# Chat history

## 2026-11-11

- **User:** can you build the program from spec.md?
- **Agent:** Interviewed for missing info. Answers: data from Open-Meteo downloaded once; fixed list of cities; exclude natural disasters entirely; plain http for now. Built `weather_data.py`, `fetch_data.py`, `app.py` (Flask), template, CSS, and tests.
- **User:** (stopped the install/test run) is flask the default for python web apps?
- **Agent:** No built-in default; compared Flask, Django, FastAPI. Explained why Flask was picked.
- **User:** lets do fastapi
- **Agent:** Switched `app.py` to FastAPI + uvicorn + jinja2, updated `requirements.txt`, `spec.md`, `arch.md`, this file.
