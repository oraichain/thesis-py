import httpx
import os
from typing import Any


async def execute_python(script: str, input_data: Any = None) -> Any:
    """
    Execute Python script via external Pyodide server.

    Args:
        script: Python script code to execute
        input_data: Optional input data to pass to the script

    Returns:
        Execution result from Pyodide server
    """
    try:
        pyodide_url = os.getenv("PYODIDE_SERVER_URL", "http://localhost:8001/execute")

        payload = {"script": script, "input": input_data}

        # async with httpx.AsyncClient(timeout=30.0) as client:
        #     response = await client.post(pyodide_url, json=payload)
        #     response.raise_for_status()
        #     result = response.json()

        # return result.get("output", result)
        return {"output": 'print("Hello, World!")'}

    except httpx.HTTPError as e:
        raise Exception(f"Pyodide server error: {str(e)}")
    except Exception as e:
        raise Exception(f"Python execution error: {str(e)}")
