import os
from thesis_py import Thesis
from thesis_py.api_schema import CreateNewConversationIntegrationRequest, ResearchMode
from thesis_py.research.events import from_raw_events_to_pairs

THESIS_API_KEY = os.environ.get("THESIS_API_KEY")

if not THESIS_API_KEY:
    raise ValueError("THESIS_API_KEY environment variable not set!")

thesis = Thesis(THESIS_API_KEY)

response = thesis.get_spaces()
print(response)

first_space_id = response.data[0].spaceId
print(first_space_id)
response = thesis.get_space_by_id(first_space_id)
print(response.data)
sections = thesis.get_space_sections(first_space_id)
print(sections.data)