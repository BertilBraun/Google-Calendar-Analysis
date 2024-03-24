from dataclasses import dataclass


@dataclass(frozen=True)
class Calendar:
    id: str
    name: str
