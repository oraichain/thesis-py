import os
from thesis_py import Thesis
from thesis_py.api_schema import CreateNewConversationIntegrationRequest, ResearchMode

THESIS_API_KEY = os.environ.get("THESIS_API_KEY")

if not THESIS_API_KEY:
    raise ValueError("THESIS_API_KEY environment variable not set!")

thesis = Thesis(THESIS_API_KEY)

response = thesis.create_conversation(
    CreateNewConversationIntegrationRequest(
        initial_user_msg="What's the new DeFi meta recently that I can ape in?",
        research_mode=ResearchMode.DEEP_RESEARCH,
        system_prompt="You are a DeFi gigachad who's always ahead of the new DeFi meta.",
    )
)

print(response)
