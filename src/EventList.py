from __future__ import annotations

from typing import Callable, TypeVar

from src.Event import Event
from src.EventGroup import EventGroup


K = TypeVar('K')


class EventList(list[Event]):
    def filter(self, condition: Callable[[Event], bool]) -> EventList:
        return EventList([event for event in self if condition(event)])

    def group_by(self, key: Callable[[Event], K]) -> EventGroup[K]:
        groups: EventGroup = EventGroup()

        for event in self:
            key_value = key(event)
            if key_value not in groups:
                groups[key_value] = EventList([])
            groups[key_value].append(event)

        # return sorted dictionary by size of the group
        return groups.sort_by(lambda group: len(group))

    def group_by_summary(self) -> EventGroup[str]:
        return self.group_by(lambda event: event.summary)

    def group_by_tokenized(self) -> EventGroup[str]:
        grouped = self.group_by(lambda event: event.tokenized)
        # map the key to the first event's summary for better readability
        return grouped.map_keys(lambda group: group[0].summary)

    def sum_duration(self) -> int:
        return sum(event.duration for event in self)
