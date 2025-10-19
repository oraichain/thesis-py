from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from openai import AsyncOpenAI
import json
from models import (
    Executable,
    SQLExecutable,
    PythonExecutable,
    LLMExecutable,
    OutputExecutable,
    CreateSQLExecutableRequest,
    CreatePythonExecutableRequest,
    CreateLLMExecutableRequest,
    CreateOutputExecutableRequest,
    GenerateSQLRequest,
    GeneratePythonScriptRequest,
    GenerateLLMPromptsRequest,
    GenerateOutputRequest,
    ExecutableType
)
from storage import storage
from config import config

router = APIRouter(prefix="/executables", tags=["executables"])


# AI Generation Endpoints

@router.post("/generate-sql", response_model=SQLExecutable)
async def generate_sql_executable(request: GenerateSQLRequest):
    """Generate SQL executable using AI with SQL-specific prompt"""
    client = AsyncOpenAI(api_key=config["OPENAI_API_KEY"])

    system_prompt = """You are an expert SQL developer specializing in DuckDB.
Generate a DuckDB SQL query based on the user's description.

Rules:
- Use DuckDB SQL dialect
- Return clean, executable SQL
- Include appropriate WHERE, ORDER BY, LIMIT clauses as needed
- Use clear column aliases
- Ensure the query is optimized and follows best practices"""

    user_prompt = f"""Generate a DuckDB SQL query for the following:

Task: {request.description}

Return ONLY the SQL query, no explanations."""

    response = await client.chat.completions.create(
        model=config["OPENAI_MODEL"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )

    generated_query = response.choices[0].message.content.strip()

    # Clean up markdown code blocks if present
    if "```sql" in generated_query:
        generated_query = generated_query.split("```sql")[1].split("```")[0].strip()
    elif "```" in generated_query:
        generated_query = generated_query.split("```")[1].split("```")[0].strip()

    # Create executable
    executable = SQLExecutable(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        query=generated_query
    )
    storage.save_executable(executable)
    return executable


@router.post("/generate-python", response_model=PythonExecutable)
async def generate_python_executable(request: GeneratePythonScriptRequest):
    """Generate Python executable using AI with Python-specific prompt.

    This generates visualization scripts (matplotlib) that accept data via sys.argv[1].
    """
    client = AsyncOpenAI(api_key=config["OPENAI_API_KEY"])

    system_prompt = """You are an expert Python developer. Generate ONLY Python code, nothing else.

CRITICAL RULES:
1. The script MUST accept data via: data = json.loads(sys.argv[1])
2. NEVER hard-code any data values from the sample
3. Parse and extract everything dynamically from the 'data' variable
4. Return ONLY executable Python code
5. NO explanations, NO markdown, NO comments about embedded data
6. Code must work with any data matching the same structure"""

    # If input_schema is provided, use it as sample data for structure analysis
    sample_data_context = ""
    if request.input_schema:
        if isinstance(request.input_schema, str):
            sample_data_context = f"\n\nSample data structure (analyze ONLY - DO NOT embed):\n{request.input_schema}"
        else:
            sample_data_context = f"\n\nSample data structure (analyze ONLY - DO NOT embed):\n{json.dumps(request.input_schema, indent=2, default=str)}"

    user_prompt = f"""Generate Python code for: {request.description}{sample_data_context}

Required structure:
```
import json
import sys
import matplotlib.pyplot as plt

data = json.loads(sys.argv[1])
# extract fields from data
# create visualization
plt.savefig('output.png')
```

REQUIREMENTS:
1. First line after imports: data = json.loads(sys.argv[1])
2. Extract all fields from 'data' variable
3. Handle the data structure shown in sample (if provided)
4. Create the visualization
5. Last line: plt.savefig('output.png')
6. NO hard-coded values

Output ONLY the Python code:"""

    response = await client.chat.completions.create(
        model=config["OPENAI_MODEL"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )

    generated_script = response.choices[0].message.content.strip()

    # Clean up markdown code blocks if present
    if "```python" in generated_script:
        generated_script = generated_script.split("```python")[1].split("```")[0].strip()
    elif "```" in generated_script:
        generated_script = generated_script.split("```")[1].split("```")[0].strip()

    # Create executable
    executable = PythonExecutable(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        script=generated_script
    )
    storage.save_executable(executable)
    return executable

@router.post("/generate-llm", response_model=LLMExecutable)
async def generate_llm_executable(request: GenerateLLMPromptsRequest):
    """Generate LLM executable using AI with prompt engineering expertise"""
    client = AsyncOpenAI(api_key=config["OPENAI_API_KEY"])

    system_prompt = """You are an expert in prompt engineering for LLMs.
Generate both a system prompt and a user prompt template for an LLM-based executable.

Rules:
- System prompt: Define the LLM's role, expertise, and behavior
- User prompt template: Create a template that can accept dynamic input via {input} placeholder
- Make prompts clear, specific, and effective
- Follow prompt engineering best practices"""

    user_prompt = f"""Generate system and user prompts for an LLM executable:

Task: {request.task_description}

Return a JSON object with two keys:
- "system_prompt": The system prompt defining the LLM's role
- "user_prompt_template": The user prompt template (use {{input}} as placeholder for dynamic data)

Example format:
{{
  "system_prompt": "You are an expert...",
  "user_prompt_template": "Analyze the following data: {{input}}"
}}"""

    response = await client.chat.completions.create(
        model=config["OPENAI_MODEL"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
    )

    prompts = json.loads(response.choices[0].message.content)

    # Create executable
    executable = LLMExecutable(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.task_description,
        system_prompt=prompts["system_prompt"],
        user_prompt_template=prompts["user_prompt_template"]
    )
    storage.save_executable(executable)
    return executable

@router.post("/generate-output", response_model=OutputExecutable)
async def generate_output_executable(request: GenerateOutputRequest):
    """Generate Output executable - just stores metadata, script generation happens at execution time"""
    # Create executable - no AI generation here
    executable = OutputExecutable(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.data_description,
        chart_type=request.chart_type
    )
    storage.save_executable(executable)
    return executable


@router.post("/sql", response_model=SQLExecutable)
async def create_sql_executable(request: CreateSQLExecutableRequest):
    """Create a new SQL executable"""
    executable = SQLExecutable(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        query=request.query
    )
    storage.save_executable(executable)
    return executable


@router.post("/python", response_model=PythonExecutable)
async def create_python_executable(request: CreatePythonExecutableRequest):
    """Create a new Python executable"""
    executable = PythonExecutable(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        script=request.script
    )
    storage.save_executable(executable)
    return executable


@router.post("/llm", response_model=LLMExecutable)
async def create_llm_executable(request: CreateLLMExecutableRequest):
    """Create a new LLM executable"""
    executable = LLMExecutable(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        system_prompt=request.system_prompt,
        user_prompt_template=request.user_prompt_template
    )
    storage.save_executable(executable)
    return executable


@router.post("/output", response_model=OutputExecutable)
async def create_output_executable(request: CreateOutputExecutableRequest):
    """Create a new Output executable"""
    executable = OutputExecutable(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.visualization_description,
        chart_type=request.chart_type
    )
    storage.save_executable(executable)
    return executable


@router.get("/{executable_id}", response_model=Executable)
async def get_executable(executable_id: str):
    """Get an executable by ID"""
    executable = storage.get_executable(executable_id)
    if not executable:
        raise HTTPException(status_code=404, detail="Executable not found")
    return executable


@router.get("/", response_model=List[Executable])
async def list_executables():
    """List all executables"""
    return storage.list_executables()
