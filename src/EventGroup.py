from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, TypeVar

if TYPE_CHECKING:
    from src.EventList import EventList

K = TypeVar('K')


class EventGroup(Dict[K, 'EventList'], Generic[K]):
    def sort_by(self, key: Callable[[EventList], Any]) -> EventGroup[K]:
        return EventGroup(sorted(self.items(), key=lambda item: key(item[1]), reverse=True))

    def map_keys(self, key: Callable[[EventList], K]) -> EventGroup:
        return EventGroup({key(v): v for k, v in self.items()})

    def filter(self, condition: Callable[[EventList], bool]) -> EventGroup[K]:
        return EventGroup({k: v for k, v in self.items() if condition(v)})
