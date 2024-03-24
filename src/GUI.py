import tkinter as tk
from datetime import datetime, timedelta

from src.Calendar import Calendar
from src.Event import Event
from src.EventList import EventGroup, EventList


class WeeklyCalendar:
    def __init__(self, events: EventGroup) -> None:
        self.master = tk.Tk()
        self.master.title('Weekly Calendar')
        self.master.geometry('800x600')
        self.year = datetime.now().year
        self.week_number = datetime.now().isocalendar()[1] + 1
        self.events = events
        self.days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Header Frame for Date Labels
        self.header_frame = tk.Frame(self.master)

        self.container = tk.Canvas(self.master, bg='white')
        self.scrollbar = tk.Scrollbar(self.master, orient='vertical', command=self.container.yview)
        self.scrollable_frame = tk.Frame(self.container)

        self.container.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame.bind('<Configure>', self.on_frame_configure)
        self.container.bind('<Configure>', self.on_canvas_configure)

        self.scrollbar.pack(side='right', fill='y')
        self.header_frame.pack(fill='x', side='top')

        self.container.pack(side='left', fill='both', expand=True)

        self.container_frame = self.container.create_window((0, 0), window=self.scrollable_frame, anchor='nw')

        self.populate_calendar()
        self.draw_events()

        self.master.bind('<MouseWheel>', self.on_mousewheel)
        self.master.bind('<Left>', self.go_to_previous_week)
        self.master.bind('<Right>', self.go_to_next_week)

        self.container.configure(scrollregion=self.container.bbox('all'))
        self.master.after(100, lambda: self.container.yview_moveto(0.33333))

        self.master.mainloop()

    def populate_calendar(self):
        start_time = 0  # Starting at 00:00 AM
        end_time = 24  # Ending at 12:00 PM

        # Create labels for time slots in 15-minute intervals in Column 0
        for hour in range(start_time, end_time):
            for quarter in range(4):
                tk.Label(
                    self.scrollable_frame,
                    text=f'{hour:02d}:{quarter*15:02d}',
                    fg='black',
                    width=10,
                    height=1,
                    anchor='e',
                ).grid(row=(hour - start_time) * 4 + quarter, column=0, sticky='ew')

        # Calculate the starting date of the specified week
        start_date = datetime.strptime(f'{self.year}-W{self.week_number-1}-1', '%G-W%V-%u')

        # Create labels for days with date
        for i, day in enumerate(self.days_of_week):
            day_date = start_date + timedelta(days=i)
            tk.Label(
                self.header_frame, text=f'{day} {day_date:%m/%d}', bg='lightgrey', fg='black', width=20, height=1
            ).grid(row=0, column=i + 1, sticky='ew')
        tk.Label(
            self.header_frame,
            text='00:00',
            fg='black',
            width=10,
            height=1,
            anchor='e',
        ).grid(row=0, column=0, sticky='ew')

        # Configure grid weights
        for i in range(1, 8):
            self.scrollable_frame.columnconfigure(i, weight=1)
        for i in range(1, 8):
            self.header_frame.columnconfigure(i, weight=1)
        for i in range((end_time - start_time) * 4 + 1):
            self.scrollable_frame.rowconfigure(i, weight=1)

    def draw_events(self):
        start_date = datetime.strptime(f'{self.year}-W{self.week_number-1}-1', '%G-W%V-%u')

        for color, events in self.events.items():
            for event in events:
                event_start = event.start.replace(tzinfo=None)
                event_end = event.end.replace(tzinfo=None)

                # Loop through each day the event might span
                current_start = event_start
                while current_start.date() <= event_end.date():
                    day_index = (current_start - start_date).days + 1
                    if 1 <= day_index <= 7:  # Check if the day is within the current week view
                        if current_start.date() == event_end.date():  # Event ends on this day
                            end_hour = event_end.hour + event_end.minute / 60
                        else:  # Event spans to the next day
                            end_hour = 24  # Go up to the end of the day

                        start_hour = current_start.hour + current_start.minute / 60
                        start_pos = int(start_hour * 4) + 1  # Convert hours to 15-min intervals
                        end_pos = int(end_hour * 4) + 1
                        row_span = end_pos - start_pos

                        # Draw event rectangles
                        event_slot = tk.Label(self.scrollable_frame, text=event.summary, bg=color, fg='black', height=1)
                        event_slot.grid(row=start_pos, column=day_index, sticky='nsew', rowspan=row_span)

                    current_start += timedelta(days=1)
                    current_start = current_start.replace(hour=0, minute=0)  # Start at the beginning of the next day

    def refresh_calendar(self):
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for widget in self.header_frame.winfo_children():
            widget.destroy()

        # Redraw the calendar
        self.populate_calendar()
        self.draw_events()

        # Adjust scroll
        self.container.configure(scrollregion=self.container.bbox('all'))
        self.container.yview_moveto(0.33333)  # Adjust the scroll position if necessary

    def go_to_previous_week(self, event=None):
        if self.week_number == 1:
            self.year -= 1
            self.week_number = 53
        self.week_number -= 1
        self.refresh_calendar()

    def go_to_next_week(self, event=None):
        if self.week_number == 52:
            self.year += 1
            self.week_number = 0
        self.week_number += 1
        self.refresh_calendar()

    def on_frame_configure(self, event=None):
        self.container.configure(scrollregion=self.container.bbox('all'))

    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.container.itemconfig('frame', width=canvas_width)
        self.container.itemconfig(self.container_frame, width=canvas_width)

    def on_mousewheel(self, event):
        self.container.yview_scroll(-1 * int(event.delta / 120), 'units')


def display_event_group(events: EventGroup) -> None:
    colors = [
        '#3498db',  # Soft Blue
        '#e67e22',  # Vivid Coral
        '#2ecc71',  # Mint Green
        '#9b59b6',  # Amethyst Purple
        '#f1c40f',  # Sunflower Yellow
        '#e74c3c',  # Tomato Red
    ]

    color_assignments = {}

    events = events.map_keys(lambda key: color_assignments.setdefault(id(key), colors.pop(0)))

    WeeklyCalendar(events)


def display_event_list(events: EventList) -> None:
    display_event_group(EventGroup({'Events': events}))


if __name__ == '__main__':
    example_events = EventList(
        [
            Event(
                summary='Event 1',
                start=datetime(2024, 3, 6, 9, 0),
                end=datetime(2024, 3, 6, 10, 45),
                id='1',
                calendar=Calendar('1', 'Calendar 1'),
                location='Location 1',
                description='Description 1',
                organizer={'email': '', 'displayName': None, 'self': None},
                creator={'email': '', 'displayName': None, 'self': None},
                updated='',
                created='',
                status='confirmed',
            ),
            Event(
                summary='Event 2',
                start=datetime(2024, 3, 7, 14, 15),
                end=datetime(2024, 3, 7, 15, 0),
                id='2',
                calendar=Calendar('2', 'Calendar 2'),
                location='Location 2',
                description='Description 2',
                organizer={'email': '', 'displayName': None, 'self': None},
                creator={'email': '', 'displayName': None, 'self': None},
                updated='',
                created='',
                status='confirmed',
            ),
        ]
    )

    event_group = EventGroup(
        {
            'Event List 1': example_events.filter(lambda e: e.summary == 'Event 1'),
            'Event List 2': example_events.filter(lambda e: e.summary == 'Event 2'),
        }
    )

    display_event_group(event_group)
