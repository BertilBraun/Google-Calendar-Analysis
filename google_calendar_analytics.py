from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json
from collections import Counter

# Initialize the Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_service():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service


def get_all_past_year_events(service):
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    last_year = (datetime.utcnow() - timedelta(days=365)).isoformat() + 'Z'

    print('Getting the past year\'s events')
    print('From: ' + last_year)
    print('To: ' + now)

    page_token = None
    events = []

    while True:
        events_result = service.events().list(calendarId='primary', timeMin=last_year,
                                              timeMax=now, pageToken=page_token, singleEvents=True,
                                              orderBy='startTime').execute()

        events.extend(events_result.get('items', []))

        page_token = events_result.get('nextPageToken')
        if not page_token:
            break

    return events


def replace_escaped_characters(text):
    replacements = {
        '\\u00f6': 'ö',
        '\\u00e4': 'ä',
        '\\u00fc': 'ü',
        '\\u00df': 'ß',
        '\\u00d6': 'Ö',
        '\\u00c4': 'Ä',
        '\\u00dc': 'Ü'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def main():
    service = get_service()
    events = get_all_past_year_events(service)

    event_names = []

    for event in events:
        event_name = event['summary']
        event_names.append(event_name)
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        duration_in_minutes = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() / 60

    event_count = Counter(event_names)
    sorted_event_count = {k: v for k, v in sorted(event_count.items(), key=lambda item: item[1], reverse=True)}

    # Replace escaped characters
    cleaned_data = {replace_escaped_characters(k): v for k, v in sorted_event_count.items()}

    # Write the cleaned and beautified data to a new JSON file
    with open('cleaned_sorted_events.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

    print("Cleaned event counts have been saved to cleaned_sorted_events.json")


if __name__ == '__main__':
    main()
