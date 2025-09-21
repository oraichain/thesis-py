from dataclasses import dataclass

from thesis_py.research.events.schema import ObservationType
from thesis_py.research.events.observation.observation import Observation


@dataclass
class MCPObservation(Observation):
    """This data class represents the result of a MCP Server operation."""

    observation: str = ObservationType.MCP
    tool_call_id: str | None = None
    name: str | None = None

    @property
    def message(self) -> str:
        return self.content
