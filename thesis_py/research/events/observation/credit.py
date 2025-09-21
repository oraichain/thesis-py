from dataclasses import dataclass

from thesis_py.research.events.schema import ObservationType
from thesis_py.research.events.observation.observation import Observation


@dataclass
class CreditErrorObservation(Observation):
    """This data class represents the result of a credit check."""

    observation: str = ObservationType.CREDIT_ERROR

    @property
    def message(self) -> str:
        return self.content
