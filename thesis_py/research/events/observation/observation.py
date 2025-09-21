from dataclasses import dataclass

from thesis_py.research.events.event import Event


@dataclass
class Observation(Event):
    content: str
