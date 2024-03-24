from datetime import datetime
from dataclasses import dataclass
from typing import TypedDict, Optional

from src.Calendar import Calendar


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
    calendar: Calendar

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
