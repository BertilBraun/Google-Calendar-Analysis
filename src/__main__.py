from src.Calendar import Calendar
from src.Client import Client
from src.EventList import EventList

from src.GUI import display_event_list


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

    display_event_list(events.filter(lambda e: 'chess' in e.summary.lower()))
