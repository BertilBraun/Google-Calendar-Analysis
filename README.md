# Google Calendar Analyzer

## Description

A simple python script to analyze your Google Calendar events.

## Requirements

- Python 3.6+
- Install the required packages with `pip install -r requirements.txt`
- Create a Google Cloud Platform project and enable the Google Calendar API
- Create and download the JSON credentials file

## Usage

- Run the script with `python google_calendar_analytics.py`
  This will open a browser window to authenticate with your Google account.
  The script will then output a json file with the events of the last year.

- Run the script with `python group_data.py` to group the events by their title and output a json file with the grouped events.
