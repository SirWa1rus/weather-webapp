# What it does

    The program will ask the user to input a location from a list of supported locations and a date (from November 10 2025 to November 10th 2026), where the program will provide these details about the weather in the inputted area on that day:

        -   hourly weather (in fahrenheit)
        -   the hi and lo of the day (in fahrenheit)
        -   if its raining, thundering, storming, etc.
        -   sunrise/sunset time

        Supported locations:

            -   Chicago
            -   Philadelphia
            -   New York
            -   Los Angeles
            -   London
            -   Paris
            -   Tokyo
            -   Sydney

# Specifications

    -   web app built in python (FastAPI)
    -   http
    -   dark gray bg
    -   curved squares that containing the info + shape of search bar
    -   databases holding data -> csv files

# CSV File Structure

    line 1: date (MM/DD/YYYY)
    line 2: hi and lo
    line 3: hourly weather (per day)
    line 4: if its raining, thundering, cloudy, partly cloudy, etc.
    line 5: sunset, sunrise time

    * data source: Open-Meteo historical archive, downloaded once
    * values stored in lists, where item n is column n
