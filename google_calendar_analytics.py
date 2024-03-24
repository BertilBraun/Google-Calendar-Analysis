from __future__ import annotations

import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, TypeVar, TypedDict, Optional


class CreatorOrOrganizer(TypedDict):
    email: str
    displayName: Optional[str]
    self: Optional[bool]


@dataclass(frozen=True)
class Event:
    id: str
    status: str
    summary: str
    description: str
    location: str
    creator: CreatorOrOrganizer
    organizer: CreatorOrOrganizer
    start: datetime
    end: datetime
    created: str
    updated: str

    @property
    def duration(self) -> int:
        """
        Calculates the duration of an event in minutes.
        :return: The duration of the event in minutes
        """
        return (self.end - self.start).seconds // 60

    @property
    def tokenized(self) -> str:
        """
        Tokenizes the summary of the event by splitting it into lowercase words, removing duplicates, removing special characters, and sorting the words.
        :return: A tokenized version of the event summary
        """
        # replace every non-alphanumeric character with a space
        summary = ''.join(c if c.isalnum() else ' ' for c in self.summary)
        # split the summary into words, convert them to lowercase, remove duplicates, and sort them
        return ' '.join(sorted(set(word.lower().strip() for word in summary.split(' '))))

    def __repr__(self) -> str:
        return self.summary


@dataclass(frozen=True)
class Calendar:
    id: str
    name: str


K = TypeVar('K')


class EventGroup(Dict[K, 'EventList'], Generic[K]):
    def sort_by(self, key: Callable[[EventList], Any]) -> EventGroup[K]:
        return EventGroup(sorted(self.items(), key=lambda item: key(item[1]), reverse=True))

    def map_keys(self, key: Callable[[EventList], K]) -> EventGroup:
        return EventGroup({key(v): v for k, v in self.items()})

    def filter(self, condition: Callable[[EventList], bool]) -> EventGroup[K]:
        return EventGroup({k: v for k, v in self.items() if condition(v)})


class EventList:
    def __init__(self, events: list[Event]) -> None:
        self.events = events

    def filter(self, condition: Callable[[Event], bool]) -> EventList:
        return EventList([event for event in self.events if condition(event)])

    def group_by(self, key: Callable[[Event], K]) -> EventGroup[K]:
        groups: EventGroup = EventGroup()

        for event in self.events:
            key_value = key(event)
            if key_value not in groups:
                groups[key_value] = EventList([])
            groups[key_value].events.append(event)

        # return sorted dictionary by size of the group
        return groups.sort_by(lambda group: len(group))

    def group_by_summary(self) -> EventGroup[str]:
        return self.group_by(lambda event: event.summary)

    def group_by_tokenized(self) -> EventGroup[str]:
        grouped = self.group_by(lambda event: event.tokenized)
        # map the key to the first event's summary for better readability
        return grouped.map_keys(lambda group: group[0].summary)

    def sum_duration(self) -> int:
        return sum(event.duration for event in self.events)

    def __iter__(self):
        return iter(self.events)

    def __len__(self):
        return len(self.events)

    def __getitem__(self, index):
        return self.events[index]

    def __repr__(self) -> str:
        return str(self.events)

    def __add__(self, other: EventList) -> EventList:
        return EventList(self.events + other.events)


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
                credentials.refresh(Request())
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

        return self.__get_events(calendar.id, time_min, time_max)

    def __get_events(self, calendar_id: str, time_min: str, time_max: str) -> EventList:
        """
        Gets all events from the specified calendar between the specified time range.
        :param calendar_id: The ID of the calendar to get events from
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
                    calendarId=calendar_id,
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
                )
                for event in events_data
            ]
        )


def select_calendar(client: Client) -> Calendar:
    """
    Displays a list of available calendars and prompts the user to select one.
    :param client: The Client object to use for fetching the calendars
    :return: The selected Calendar object
    """
    calendars = client.get_calendars()

    print('Available calendars:')
    for i, calendar in enumerate(calendars):
        print(f'{i + 1}. {calendar.name}')

    calendar = calendars[int(input('Enter the number of the calendar you want to analyze: ')) - 1]
    return calendar


def get_events_in_last_year_from_user_chosen_calendar() -> EventList:
    client = Client()
    calendar = select_calendar(client)
    events = client.get_events_within_days(calendar, days_in_past=365)
    return events


def get_events_in_last_year_from_all_calendars() -> EventList:
    client = Client()
    calendars = client.get_calendars()
    events = EventList([])
    for calendar in calendars:
        events += client.get_events_within_days(calendar, days_in_past=365)
    return events


if __name__ == '__main__':
    # events = get_events_in_last_year_from_user_chosen_calendar()
    events = get_events_in_last_year_from_all_calendars()

    total_time_spent = events.sum_duration()
    print(f'Total time spent on all events: {total_time_spent} minutes')

    grouped_events = (
        events.group_by_tokenized().filter(lambda group: len(group) > 5).sort_by(lambda group: -group.sum_duration())
    )
    print('Events with more than 5 occurrences:')
    for event_name, group in grouped_events.items():
        print(f'{event_name}: {len(group)} times, {group.sum_duration()} minutes')

    total_time_for_chess = events.filter(lambda e: 'chess' in e.summary.lower()).sum_duration()
    print(f'Total time spent on Chess: {total_time_for_chess} minutes')
