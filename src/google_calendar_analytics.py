import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json
from collections import Counter

from .types import Event, Calendar

# Initialize the Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_service():
    """
    Creates a Google Calendar API service object with the login credentials of the user.
    :return: The service object for the Google Calendar API
    """

    credentials = None
    if os.path.exists('token.json'):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        credentials = Credentials.from_authorized_user_file('token.json')

    if not credentials or not credentials.valid:
        # If there are no (valid) credentials available, let the user log in.
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(credentials.to_json())

    service = build('calendar', 'v3', credentials=credentials)
    return service


def get_calendars(service) -> list[Calendar]:
    """
    Fetches all available calendars for the user, including their names and IDs.
    :param service: The authenticated Google Calendar API service object.
    :return: A list of dictionaries, each containing the 'name' and 'id' of a calendar.
    """
    calendars: list[Calendar] = []
    page_token = None

    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list.get('items', []):
            calendars.append(Calendar(id=calendar_list_entry['id'], name=calendar_list_entry.get('summary', 'No Name')))

        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    return calendars


def get_events(service, calendar_id: str, time_min: str, time_max: str) -> list[Event]:
    """
    Gets all events from the specified calendar between the specified time range.
    :param service: The Google Calendar API service object
    :param calendar_id: The ID of the calendar to get events from
    :param time_min: The minimum time of the events to get
    :param time_max: The maximum time of the events to get
    :return: A list of all events in the specified time range
    """

    page_token = None
    events = []

    while True:
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                pageToken=page_token,
                singleEvents=True,
                orderBy='startTime',
            )
            .execute()
        )

        events.extend(events_result.get('items', []))

        page_token = events_result.get('nextPageToken')
        if not page_token:
            break

    return events


def get_events_within_days(service, calendar_id: str, days_in_future: int = 0, days_in_past: int = 0) -> list[Event]:
    # 'Z' indicates UTC time
    time_max = (datetime.utcnow() + timedelta(days=days_in_future)).isoformat() + 'Z'
    time_min = (datetime.utcnow() - timedelta(days=days_in_past)).isoformat() + 'Z'

    return get_events(service, calendar_id, time_min, time_max)


def get_event_duration(event: Event) -> int:
    """
    Calculates the duration of an event in minutes.
    :param event: The event to calculate the duration for
    :return: The duration of the event in minutes
    """
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() // 60  # type: ignore


def main():
    service = get_service()

    calendars = get_calendars(service)

    print('Available calendars:')
    for i, calendar in enumerate(calendars):
        print(f'{i + 1}. {calendar.name}')

    calendar_id = calendars[int(input('Enter the number of the calendar you want to analyze: ')) - 1].id

    event_names = []
    event_durations = []

    for event in get_events_within_days(service, calendar_id, days_in_past=365):
        event_name = event['summary']
        duration_in_minutes = get_event_duration(event)

        event_names.append(event_name)
        event_durations.append(duration_in_minutes)

    total_pst_time = sum(
        duration for name, duration in zip(event_names, event_durations) if 'PST' in name or 'Praktikum ST' in name
    )

    print('Total PST time: ' + str(total_pst_time) + ' minutes')

    event_count = Counter(event_names)
    sorted_event_count = {k: v for k, v in sorted(event_count.items(), key=lambda item: item[1], reverse=True)}

    print('Event counts:')
    for event, count in sorted_event_count.items():
        print(f'{event}: {count} times')

    # Write the cleaned and beautified data to a new JSON file
    with open('cleaned_sorted_events.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_event_count, f, indent=4, ensure_ascii=False)

    print('Cleaned event counts have been saved to cleaned_sorted_events.json')


if __name__ == '__main__':
    main()
