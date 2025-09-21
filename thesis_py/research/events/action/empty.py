from dataclasses import dataclass

from thesis_py.research.events.schema.action import ActionType
from thesis_py.research.events.action.action import Action


@dataclass
class NullAction(Action):
    """An action that does nothing."""

    action: str = ActionType.NULL

    @property
    def message(self) -> str:
        return 'No action'
