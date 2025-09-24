import os
from thesis_py import Thesis
from thesis_py.api_schema import CreateNewConversationIntegrationRequest, ResearchMode
from thesis_py.research.events import from_raw_events_to_pairs

THESIS_API_KEY = os.environ.get("THESIS_API_KEY")

if not THESIS_API_KEY:
    raise ValueError("THESIS_API_KEY environment variable not set!")

thesis = Thesis(THESIS_API_KEY)

response = thesis.get_conversation_by_id(os.environ.get("THESIS_CONVERSATION_ID"))

pairs = from_raw_events_to_pairs(response.events[:2])

print(pairs)
