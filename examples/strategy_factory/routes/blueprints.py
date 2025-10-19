from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from models import (
    Blueprint,
    CreateBlueprintRequest,
    UpdateStepsRequest,
)
from storage import storage

router = APIRouter(prefix="/blueprints", tags=["blueprints"])


@router.post("/", response_model=Blueprint)
async def create_blueprint(request: CreateBlueprintRequest):
    """Create a new blueprint"""
    # Validate that all executable IDs exist
    executables = {}
    for exec_id in request.executable_ids:
        executable = storage.get_executable(exec_id)
        if not executable:
            raise HTTPException(
                status_code=404,
                detail=f"Executable {exec_id} not found"
            )
        executables[exec_id] = executable

    # Validate steps - ensure all executable IDs in steps exist
    for step in request.steps:
        for exec_id in step.executable_ids:
            if exec_id not in request.executable_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Step references unknown executable: {exec_id}"
                )

    # Create blueprint
    blueprint = Blueprint(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        executables=executables,
        steps=request.steps
    )

    storage.save_blueprint(blueprint)
    return blueprint


@router.get("/{blueprint_id}", response_model=Blueprint)
async def get_blueprint(blueprint_id: str):
    """Get a blueprint by ID"""
    blueprint = storage.get_blueprint(blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    return blueprint


@router.get("/", response_model=List[Blueprint])
async def list_blueprints():
    """List all blueprints"""
    return storage.list_blueprints()


@router.patch("/{blueprint_id}/steps", response_model=Blueprint)
async def update_steps(blueprint_id: str, request: UpdateStepsRequest):
    """Update blueprint execution steps"""
    blueprint = storage.get_blueprint(blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    # Validate new steps
    for step in request.steps:
        for exec_id in step.executable_ids:
            if exec_id not in blueprint.executables:
                raise HTTPException(
                    status_code=400,
                    detail=f"Step references unknown executable: {exec_id}"
                )

    # Update steps
    blueprint.steps = request.steps
    storage.save_blueprint(blueprint)
    return blueprint
