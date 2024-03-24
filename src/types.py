from dataclasses import dataclass
from typing import TypedDict, Optional


class CreatorOrOrganizer(TypedDict):
    email: str
    displayName: Optional[str]
    self: Optional[bool]


class DateTime(TypedDict):
    dateTime: str
    timeZone: str


class Date(TypedDict):
    date: str


class ExtendedProperties(TypedDict):
    private: dict


class Reminders(TypedDict):
    useDefault: bool


class Source(TypedDict):
    url: str
    title: str


class Event(TypedDict):
    kind: str
    etag: str
    id: str
    status: str
    htmlLink: str
    created: str
    updated: str
    summary: str
    description: str
    location: str
    creator: CreatorOrOrganizer
    organizer: CreatorOrOrganizer
    start: DateTime | Date
    end: DateTime | Date
    iCalUID: str
    sequence: int
    extendedProperties: ExtendedProperties
    reminders: Reminders
    source: Source
    eventType: str


@dataclass
class Calendar:
    id: str
    name: str
