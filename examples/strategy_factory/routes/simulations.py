from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from openai import AsyncOpenAI
import json
from datetime import datetime
from models import (
    Simulation,
    CreateSimulationRequest,
    GenerateInputRequest,
    RefineInputRequest,
    ExecuteSimulationResponse,
    ExecutionStatus,
    ChatMessage
)
from storage import storage
from engine import run_simulation
from config import config

router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.post("/", response_model=Simulation)
async def create_simulation(request: CreateSimulationRequest):
    """Create a new simulation for a blueprint"""
    blueprint = storage.get_blueprint(request.blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    simulation = Simulation(
        id=str(uuid.uuid4()),
        blueprint_id=request.blueprint_id
    )

    storage.save_simulation(simulation)
    return simulation


@router.post("/{simulation_id}/generate-input", response_model=Simulation)
async def generate_input(simulation_id: str, request: GenerateInputRequest):
    """Generate input for a specific executable using AI"""
    simulation = storage.get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    blueprint = storage.get_blueprint(simulation.blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    # Check if executable exists in blueprint
    executable = blueprint.executables.get(request.executable_id)
    if not executable:
        raise HTTPException(status_code=404, detail="Executable not found in blueprint")

    client = AsyncOpenAI(api_key=config["OPENAI_API_KEY"])

    system_prompt = """You are an expert at generating realistic test data for data analysis pipelines.
Generate appropriate input data for the specified executable based on its type and description.

Return a JSON object representing the input data for this executable."""

    user_prompt = f"""Executable: {executable.name}
Type: {executable.type.value}
Description: {executable.description}

Generate realistic input data for this executable. The data should be appropriate for its type:
- For SQL executables: can be null or sample data to query
- For Python executables: sample data to process
- For LLM executables: context or data to analyze
- For Output executables: this will receive data from previous steps, so can be null

Return only the input data as JSON."""

    response = await client.chat.completions.create(
        model=config["OPENAI_MODEL"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    input_data = json.loads(response.choices[0].message.content)

    # Update simulation inputs for this executable
    if not simulation.inputs:
        simulation.inputs = {}
    simulation.inputs[request.executable_id] = input_data
    simulation.updated_at = datetime.utcnow()
    storage.save_simulation(simulation)

    return simulation


@router.post("/{simulation_id}/refine-input", response_model=Simulation)
async def refine_input(simulation_id: str, request: RefineInputRequest):
    """Refine input for a specific executable through conversational AI"""
    simulation = storage.get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    blueprint = storage.get_blueprint(simulation.blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    # Check if executable exists in blueprint
    executable = blueprint.executables.get(request.executable_id)
    if not executable:
        raise HTTPException(status_code=404, detail="Executable not found in blueprint")

    client = AsyncOpenAI(api_key=config["OPENAI_API_KEY"])

    # Get current input for this executable
    current_input = simulation.inputs.get(request.executable_id, None)

    # Build conversation history for this specific executable
    # Store chat history per executable
    if not hasattr(simulation, 'executable_chat_history'):
        simulation.executable_chat_history = {}

    exec_chat_key = request.executable_id
    if exec_chat_key not in simulation.chat_history:
        # Initialize chat history for this executable if it doesn't exist
        exec_chat_history = []
    else:
        # Get existing chat history (we'll use the main chat_history with a prefix for now)
        exec_chat_history = [msg for msg in simulation.chat_history if msg.content.startswith(f"[{request.executable_id}]")]

    messages = [
        {
            "role": "system",
            "content": f"""You are an expert assistant helping refine test data for a specific executable in a data analysis pipeline.
The user will ask you to modify the input data for this executable. Make the requested changes and return the updated input as JSON.

Executable: {executable.name}
Type: {executable.type.value}
Description: {executable.description}

Always return a valid JSON object representing the input data for this executable."""
        }
    ]

    # Add current input context
    if current_input is not None:
        messages.append({
            "role": "user",
            "content": f"""Current input data:
{json.dumps(current_input, indent=2)}"""
        })

    # Add chat history for this executable
    for msg in exec_chat_history:
        # Remove the prefix from stored messages
        content = msg.content.replace(f"[{request.executable_id}] ", "")
        messages.append({"role": msg.role, "content": content})

    # Add user's refinement request
    messages.append({"role": "user", "content": request.message})

    response = await client.chat.completions.create(
        model=config["OPENAI_MODEL"],
        messages=messages,
        response_format={"type": "json_object"}
    )

    assistant_message = response.choices[0].message.content

    # Parse updated input
    try:
        updated_input = json.loads(assistant_message)
        if not simulation.inputs:
            simulation.inputs = {}
        simulation.inputs[request.executable_id] = updated_input
    except json.JSONDecodeError:
        # If response is not valid JSON, keep the old input
        pass

    # Update chat history with executable prefix
    simulation.chat_history.append(ChatMessage(role="user", content=f"[{request.executable_id}] {request.message}"))
    simulation.chat_history.append(ChatMessage(role="assistant", content=f"[{request.executable_id}] {assistant_message}"))
    simulation.updated_at = datetime.utcnow()

    storage.save_simulation(simulation)
    return simulation


@router.post("/{simulation_id}/execute", response_model=ExecuteSimulationResponse)
async def execute_simulation(simulation_id: str):
    """Execute the simulation"""
    simulation = storage.get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    blueprint = storage.get_blueprint(simulation.blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    try:
        # Update status
        simulation.status = ExecutionStatus.RUNNING
        simulation.updated_at = datetime.utcnow()
        storage.save_simulation(simulation)

        # Execute
        results = await run_simulation(blueprint, simulation)

        # Update with results
        simulation.status = ExecutionStatus.COMPLETED
        simulation.results = results
        simulation.updated_at = datetime.utcnow()
        storage.save_simulation(simulation)

        return ExecuteSimulationResponse(
            simulation_id=simulation_id,
            status=ExecutionStatus.COMPLETED,
            message="Simulation completed successfully"
        )

    except Exception as e:
        simulation.status = ExecutionStatus.FAILED
        simulation.error = str(e)
        simulation.updated_at = datetime.utcnow()
        storage.save_simulation(simulation)

        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/{simulation_id}/status", response_model=Simulation)
async def get_simulation_status(simulation_id: str):
    """Get simulation status"""
    simulation = storage.get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation


@router.get("/{simulation_id}/results")
async def get_simulation_results(simulation_id: str):
    """Get simulation execution results"""
    simulation = storage.get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if simulation.status != ExecutionStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Simulation is not completed. Current status: {simulation.status}"
        )

    return simulation.results


@router.get("/", response_model=List[Simulation])
async def list_simulations():
    """List all simulations"""
    return storage.list_simulations()
