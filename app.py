"""The web app. Run:  python app.py   then open http://127.0.0.1:8000"""

from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import weather_data

HERE = Path(__file__).parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request, city: str = "", date: str = ""):
    # FastAPI fills 'city' and 'date' from the URL: /?city=Chicago&date=2025-11-10
    weather, error = None, None
    if city or date:  # only search after the form was submitted
        try:
            weather = weather_data.lookup(city, date)
        except weather_data.WeatherError as e:
            error = str(e)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "cities": weather_data.available_cities(),
            "city": city,
            "date_text": date,
            "min_date": weather_data.FIRST_DATE.isoformat(),
            "max_date": weather_data.LAST_DATE.isoformat(),
            "weather": weather,
            "error": error,
        },
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
