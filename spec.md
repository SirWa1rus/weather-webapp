# What it does

    The program will ask the user to input a location (Chicago, Philadelphia, London, etc) and a date (from November 10 2025 to November 10th 2026), where the program will provide these details about the weather in the inputted area on that day:

        -   hourly weather (in fahrenheit)
        -   the hi and lo of the day (in fahrenheit)
        -   if its raning, thundering, storming, etc.
        -   if there is a natural disaster present
        -   sunrise/sunset time

# Specifications

    -   web app built in python
    -   https
    -   dark gray bg
    -   curved squares that containing the info + shape of search bar
    -   databases holding data -> csv files

# CSV File Structure

    line 1: date (MM/DD/YYYY)
    line 2: hi and lo
    line 3: hourly weather (per day)
    line 4: if its raining, thundering, cloudy, partly cloudy, etc.
    line 5: natural disaster (fill with -999 if not applicable)
    line 6: sunset, sunrise time

    * values stored in lists, where item n is column n
