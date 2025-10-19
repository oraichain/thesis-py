from openai import AsyncOpenAI
from typing import Any
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config


async def execute_llm(
    system_prompt: str, user_prompt_template: str, input_data: Any = None
) -> str:
    """
    Execute LLM call using OpenAI API.

    Args:
        system_prompt: System prompt for the LLM
        user_prompt_template: User prompt template (can include {input} placeholder)
        input_data: Optional input data to inject into the prompt

    Returns:
        LLM response as text
    """
    try:
        client = AsyncOpenAI(api_key=config["OPENAI_API_KEY"])

        # Format user prompt with input data
        if input_data is not None:
            # Convert input_data to JSON string for injection
            if isinstance(input_data, (dict, list)):
                input_str = json.dumps(input_data, indent=2)
            else:
                input_str = str(input_data)

            user_prompt = user_prompt_template.replace("{input}", input_str)
        else:
            user_prompt = user_prompt_template

        # Call OpenAI API
        response = await client.chat.completions.create(
            model=config["OPENAI_MODEL"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"LLM execution error: {str(e)}")
