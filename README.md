# Google Calendar Analyzer

## Description

This project is a comprehensive Python application for analyzing Google Calendar events. It offers functionalities to fetch events from specified time periods, categorize them by various criteria, and perform aggregate analyses such as summing up the total duration of events. It supports analyzing events from both specific calendars chosen by the user and all calendars available to the user's account.

## Features

- Fetch events from a user-selected calendar or all calendars associated with the user's Google account.
- Analyze events within a specified time frame, focusing on the last year as the default.
- Group events by their summaries or a tokenized form of their summaries for better categorization.
- Calculate the total duration of events to quantify time spent on various activities.
- Filter and sort event groups based on criteria such as the number of occurrences and total duration.

## Requirements

- Python 3.6 or later.
- Google Calendar API enabled on your Google Cloud Platform project.
- OAuth 2.0 Client ID credentials in the form of a downloaded JSON file.

## Setup

1. **Install Dependencies**: Install the required Python packages with the following command:

   ```bash
   pip install -r requirements.txt
   ```

2. **Google Cloud Platform Configuration**:
   - Create a new project in the Google Cloud Platform Console.
   - Enable the Google Calendar API for your project.
   - Create credentials (OAuth 2.0 Client ID) for your project and download the JSON file.

3. **Authentication Setup**:
   - Place the downloaded JSON credentials file in your project directory and rename it to `credentials.json`.
   - The first time you run the script, it will prompt you to authenticate via a web browser and will store the access tokens in `token.json` for subsequent uses.

## Usage

### Running the Analyzer

Execute the script with the following command:

```bash
python -m src
```

Upon the first run, you will be prompted to authenticate with your Google account through a web browser. This step authorizes the application to access your Google Calendar events.

### Analyzing Events

After authentication, the script automatically fetches events from the last year across all your calendars, calculates the total time spent on all events, and displays the aggregated information on events with more than 5 occurrences.

You can customize the script to analyze a specific calendar by uncommenting the line:

```python
# events = get_events_in_last_year_from_user_chosen_calendar()
```

and commenting out the line:

```python
events = get_events_in_last_year_from_all_calendars()
```

### Further Customization

The project's classes and functions are designed to be modular, allowing further customization, such as analyzing events based on different criteria or time frames.

## Example Usage

This section outlines a basic example of how to perform custom analyses on your Google Calendar events using the project's functionality. The example demonstrates how to filter events, group them, and aggregate data to extract meaningful insights.

### Analyzing Time Spent on Specific Types of Events

Suppose you want to analyze the total time spent on "Meetings" versus "Personal" events over the last year. Here’s how you could approach this:

```python
# Initialize the client and fetch events from the last year
client = Client()
events = client.get_events_within_days(calendar, days_in_past=365)

# Filter events containing 'Meeting' in their summaries
meeting_events = events.filter(lambda e: 'meeting' in e.summary.lower())

# Similarly, filter for personal events
personal_events = events.filter(lambda e: 'personal' in e.summary.lower())

# Aggregate the total duration of these events
total_meeting_time = meeting_events.sum_duration()
total_personal_time = personal_events.sum_duration()

print(f"Total time spent in meetings: {total_meeting_time} minutes")
print(f"Total time on personal events: {total_personal_time} minutes")
```

### Advanced Grouping and Analysis

For a more advanced analysis, let’s group events by their summaries, filter out those with fewer than 5 occurrences to focus on frequent event types, and then sort these groups by their total duration:

```python
# Group events by their tokenized summaries for a broad categorization
grouped_events = events.group_by_tokenized()

# Filter groups with more than 5 occurrences to focus on frequent events
frequent_events = grouped_events.filter(lambda group: len(group) > 5)

# Sort these groups by their total duration to see where most time is spent
sorted_events = frequent_events.sort_by(lambda group: -group.sum_duration())

# Display the sorted groups and their total durations
for event_name, group in sorted_events.items():
    print(f"{event_name}: {len(group)} times, {group.sum_duration()} minutes")
```

These examples illustrate the flexibility of the project in performing custom analyses. Users can modify these snippets to fit their specific needs, such as analyzing different time frames, focusing on other types of events, or applying different criteria for grouping and filtering.

### Graphical Representation

The project also supports graphical representation of the analyzed data. You can visualize a filtered, sorted or grouped set of events using the `display_event_list` or `display_event_group` functions in a calendar format based on tkinter. Here's an example:

```python
events = get_events_in_last_year_from_all_calendars()

# Display all meeting events from the last year in a calendar
display_event_list(events.filter(lambda e: 'meeting' in e.summary.lower()))
```

## Contributing

Contributions to the project are welcome. Please feel free to fork the repository, make your changes, and submit a pull request.
