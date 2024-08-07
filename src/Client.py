import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from datetime import datetime, timedelta

from src.Calendar import Calendar
from src.Event import Event
from src.EventList import EventList


class Client:
    def __init__(self) -> None:
        self.service = self.get_service()

    @staticmethod
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
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    print(f'Error refreshing credentials: {e}')
                    os.remove('token.json')
                    return Client.get_service()
            else:
                # Initialize the Calendar API
                SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                credentials = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())

        service = build('calendar', 'v3', credentials=credentials)
        return service

    def get_calendars(self) -> list[Calendar]:
        """
        Fetches all available calendars for the user, including their names and IDs.
        :return: A list of dictionaries, each containing the 'name' and 'id' of a calendar.
        """
        calendars: list[Calendar] = []
        page_token = None

        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list.get('items', []):
                calendars.append(
                    Calendar(id=calendar_list_entry['id'], name=calendar_list_entry.get('summary', 'No Name'))
                )

            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        return calendars

    def get_events_within_days(self, calendar: Calendar, days_in_future: int = 0, days_in_past: int = 0) -> EventList:
        """
        Gets all events from the specified calendar within a specified number of days in the future and past.
        :param calendar: The Calendar to get events from
        :param days_in_future: The number of days in the future to get events from
        :param days_in_past: The number of days in the past to get events from
        :return: A list of all events within the specified time range
        """
        assert days_in_future >= 0, 'days_in_future must be a non-negative integer'
        assert days_in_past >= 0, 'days_in_past must be a non-negative integer'

        # 'Z' indicates UTC time
        time_max = (datetime.utcnow() + timedelta(days=days_in_future)).isoformat() + 'Z'
        time_min = (datetime.utcnow() - timedelta(days=days_in_past)).isoformat() + 'Z'

        return self.__get_events(calendar, time_min, time_max)

    def __get_events(self, calendar: Calendar, time_min: str, time_max: str) -> EventList:
        """
        Gets all events from the specified calendar between the specified time range.
        :param calendar: The Calendar to get events from
        :param time_min: The minimum time of the events to get
        :param time_max: The maximum time of the events to get
        :return: A list of all events in the specified time range
        """

        page_token = None
        events_data = []

        while True:
            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar.id,
                    timeMin=time_min,
                    timeMax=time_max,
                    pageToken=page_token,
                    singleEvents=True,
                    orderBy='startTime',
                )
                .execute()
            )

            events_data.extend(events_result.get('items', []))

            page_token = events_result.get('nextPageToken')
            if not page_token:
                break

        return EventList(
            [
                Event(
                    id=event['id'],
                    status=event['status'],
                    summary=event['summary'],
                    description=event.get('description', ''),
                    location=event.get('location', ''),
                    creator=event['creator'],
                    organizer=event['organizer'],
                    start=datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date'))),
                    end=datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date'))),
                    created=event['created'],
                    updated=event['updated'],
                    calendar=calendar,
                )
                for event in events_data
            ]
        )
