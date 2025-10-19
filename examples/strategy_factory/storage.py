from typing import Optional, List, Dict
from models import Executable, Blueprint, Simulation


class Storage:
    """In-memory storage for executables, blueprints, and simulations"""

    def __init__(self):
        self.executables: Dict[str, Executable] = {}
        self.blueprints: Dict[str, Blueprint] = {}
        self.simulations: Dict[str, Simulation] = {}

    # Executable operations
    def save_executable(self, executable: Executable):
        self.executables[executable.id] = executable

    def get_executable(self, executable_id: str) -> Optional[Executable]:
        return self.executables.get(executable_id)

    def list_executables(self) -> List[Executable]:
        return list(self.executables.values())

    # Blueprint operations
    def save_blueprint(self, blueprint: Blueprint):
        self.blueprints[blueprint.id] = blueprint

    def get_blueprint(self, blueprint_id: str) -> Optional[Blueprint]:
        return self.blueprints.get(blueprint_id)

    def list_blueprints(self) -> List[Blueprint]:
        return list(self.blueprints.values())

    # Simulation operations
    def save_simulation(self, simulation: Simulation):
        self.simulations[simulation.id] = simulation

    def get_simulation(self, simulation_id: str) -> Optional[Simulation]:
        return self.simulations.get(simulation_id)

    def list_simulations(self) -> List[Simulation]:
        return list(self.simulations.values())


# Global storage instance
storage = Storage()
