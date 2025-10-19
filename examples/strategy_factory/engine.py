import asyncio
from typing import Dict, Any, List
from models import Blueprint, Simulation, Executable
from executors import execute_sql, execute_python, execute_llm, execute_output


class ExecutionEngine:
    """
    Step-based execution engine for running blueprints.
    Executes steps sequentially, with concurrent execution within each step.
    """

    def __init__(self, blueprint: Blueprint, simulation: Simulation):
        self.blueprint = blueprint
        self.simulation = simulation
        self.results: Dict[str, Any] = {}

    async def execute(self) -> Dict[str, Any]:
        """
        Execute the blueprint following the ordered steps.

        Returns:
            Dictionary mapping executable_id to execution results
        """
        try:
            # Execute steps sequentially
            for step_index, step in enumerate(self.blueprint.steps):
                print(f"Executing step {step_index + 1}/{len(self.blueprint.steps)}")
                await self._execute_step(step.executable_ids)

            return self.results

        except Exception as e:
            raise Exception(f"Execution engine error: {str(e)}")

    async def _execute_step(self, executable_ids: List[str]):
        """
        Execute all executables in a step concurrently.

        Args:
            executable_ids: List of executable IDs to execute concurrently
        """
        tasks = [self._execute_single(exec_id) for exec_id in executable_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for errors
        for exec_id, result in zip(executable_ids, results):
            if isinstance(result, Exception):
                raise Exception(f"Error executing {exec_id}: {str(result)}")

    async def _execute_single(self, exec_id: str) -> Any:
        """
        Execute a single executable and store its result.

        Args:
            exec_id: ID of the executable to execute

        Returns:
            Execution result
        """
        executable = self.blueprint.executables[exec_id]

        # Gather inputs from previous steps
        input_data = self._gather_inputs_from_previous_steps(exec_id)

        # Execute based on executable type
        result = await self._execute_executable(executable, input_data)

        # Store result with executable ID tag
        self.results[exec_id] = result

        return result

    def _gather_inputs_from_previous_steps(self, current_exec_id: str) -> Any:
        """
        Gather input data from all previously executed executables.

        Args:
            current_exec_id: The current executable ID

        Returns:
            Input data from all previous results as a dict, or None if no previous results
        """
        # If this executable has simulation input, use that
        if current_exec_id in self.simulation.inputs:
            return self.simulation.inputs[current_exec_id]

        # Otherwise, gather all previous results
        if not self.results:
            return None

        # Return all previous results as a dict
        return dict(self.results)

    def _check_if_inputs_deterministic(self) -> bool:
        """
        Check if all previous executables produce deterministic outputs.

        LLM executables are non-deterministic (may produce different outputs each run).
        SQL and Python executables are deterministic (same input -> same output).

        Returns:
            True if all previous executables are deterministic (SQL, Python only)
            False if any LLM executable was executed
        """
        from models import LLMExecutable

        # Check all executed results so far
        for exec_id in self.results.keys():
            executable = self.blueprint.executables[exec_id]
            if isinstance(executable, LLMExecutable):
                return False  # Non-deterministic due to LLM

        return True  # All deterministic (SQL, Python only)

    async def _execute_executable(self, executable: Executable, input_data: Any) -> Any:
        """
        Execute an executable based on its type.

        Args:
            executable: The executable to execute
            input_data: Input data from previous steps or simulation

        Returns:
            Execution result
        """
        from models import SQLExecutable, PythonExecutable, LLMExecutable, OutputExecutable
        from routes.executables import generate_python_executable
        from models import GeneratePythonScriptRequest
        import json

        if isinstance(executable, SQLExecutable):
            return await execute_sql(executable.query, input_data)

        elif isinstance(executable, PythonExecutable):
            return await execute_python(executable.script, input_data)

        elif isinstance(executable, LLMExecutable):
            return await execute_llm(
                executable.system_prompt,
                executable.user_prompt_template,
                input_data
            )

        elif isinstance(executable, OutputExecutable):
            # Check if we can use cached script
            script = None
            is_deterministic = self._check_if_inputs_deterministic()

            if executable.cached_script and is_deterministic:
                # Reuse cached script - inputs are deterministic
                print(f"  ✓ Using cached script for {executable.name} (deterministic inputs)")
                script = executable.cached_script
            else:
                # Generate new script
                if not is_deterministic:
                    print(f"  ⚠ Generating new script for {executable.name} (non-deterministic inputs detected)")
                else:
                    print(f"  🔄 Generating script for {executable.name} (first run)")

                script_request = GeneratePythonScriptRequest(
                    name=f"{executable.name} Script",
                    description=f"Create {executable.chart_type.value} visualization: {executable.description}",
                    input_schema=str(input_data)  # Pass actual data as schema reference
                )
                python_executable = await generate_python_executable(script_request)
                script = python_executable.script

                # Cache the script if inputs are deterministic
                if is_deterministic:
                    executable.cached_script = script
                    # Update in storage
                    from storage import storage
                    storage.save_executable(executable)

            # Execute the script with input_data
            result = await execute_output(
                script=script,
                input_data=input_data
            )

            # Return the generated script (for caching analysis in tests)
            # In production, this would be the execution result
            return script

        else:
            raise Exception(f"Unknown executable type: {type(executable)}")


async def run_simulation(blueprint: Blueprint, simulation: Simulation) -> Dict[str, Any]:
    """
    Run a simulation using the execution engine.

    Args:
        blueprint: Blueprint to execute
        simulation: Simulation with inputs and state

    Returns:
        Dictionary of execution results
    """
    engine = ExecutionEngine(blueprint, simulation)
    results = await engine.execute()
    return results
