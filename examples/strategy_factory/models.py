from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
from enum import Enum


class ExecutableType(str, Enum):
    SQL = "sql"
    PYTHON = "python"
    LLM = "llm"
    OUTPUT = "output"


class ChartType(str, Enum):
    TABLE = "table"
    MARKDOWN = "markdown"
    AREA_CHART = "area_chart"
    NUMBER = "number"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"


# Base Executable Models
class ExecutableBase(BaseModel):
    id: str
    type: ExecutableType
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SQLExecutable(ExecutableBase):
    type: Literal[ExecutableType.SQL] = ExecutableType.SQL
    query: str


class PythonExecutable(ExecutableBase):
    type: Literal[ExecutableType.PYTHON] = ExecutableType.PYTHON
    script: str


class LLMExecutable(ExecutableBase):
    type: Literal[ExecutableType.LLM] = ExecutableType.LLM
    system_prompt: str
    user_prompt_template: str  # Can include {input} placeholder


class OutputExecutable(ExecutableBase):
    type: Literal[ExecutableType.OUTPUT] = ExecutableType.OUTPUT
    chart_type: ChartType
    description: str  # Description of what to visualize
    cached_script: Optional[str] = None  # Cached Python script (for deterministic inputs)


# Union type for all executables
Executable = SQLExecutable | PythonExecutable | LLMExecutable | OutputExecutable


# Execution Step Model
class ExecutionStep(BaseModel):
    """A step in the blueprint execution. Each step can have multiple executables running concurrently."""
    executable_ids: List[str]  # List of executable IDs to run concurrently in this step


# Blueprint Model
class Blueprint(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    executables: Dict[str, Executable]  # executable_id -> Executable
    steps: List[ExecutionStep]  # Ordered list of execution steps
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Simulation Models
class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationInput(BaseModel):
    executable_id: str
    input_data: Any


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class Simulation(BaseModel):
    id: str
    blueprint_id: str
    inputs: Dict[str, Any] = {}  # executable_id -> input data
    chat_history: List[ChatMessage] = []  # For conversational refinement
    status: ExecutionStatus = ExecutionStatus.PENDING
    results: Dict[str, Any] = {}  # executable_id -> execution result
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response Models
class GenerateSQLRequest(BaseModel):
    name: str
    description: str  # What data to query


class GeneratePythonScriptRequest(BaseModel):
    name: str
    description: str  # What the script should do
    input_schema: Optional[str] = None  # Description of expected input


class GenerateLLMPromptsRequest(BaseModel):
    name: str
    task_description: str  # What the LLM should accomplish


class GenerateOutputRequest(BaseModel):
    name: str
    chart_type: ChartType
    data_description: str  # Description of the data to visualize


class CreateSQLExecutableRequest(BaseModel):
    name: str
    description: Optional[str] = None
    query: str


class CreatePythonExecutableRequest(BaseModel):
    name: str
    description: Optional[str] = None
    script: str


class CreateLLMExecutableRequest(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    user_prompt_template: str


class CreateOutputExecutableRequest(BaseModel):
    name: str
    description: Optional[str] = None
    chart_type: ChartType
    visualization_description: str


class CreateBlueprintRequest(BaseModel):
    name: str
    description: Optional[str] = None
    executable_ids: List[str]
    steps: List[ExecutionStep]  # Ordered execution steps


class UpdateStepsRequest(BaseModel):
    steps: List[ExecutionStep]  # New ordered execution steps


class CreateSimulationRequest(BaseModel):
    blueprint_id: str


class GenerateInputRequest(BaseModel):
    executable_id: str


class RefineInputRequest(BaseModel):
    executable_id: str
    message: str


class ExecuteSimulationResponse(BaseModel):
    simulation_id: str
    status: ExecutionStatus
    message: str
