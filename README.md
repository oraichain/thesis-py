# Thesis.io Python SDK

A Python client for interacting with the Thesis.io API, enabling conversations, research, and space management.

## Installation

```bash
pip install thesis_py
```

## Quick Start

Initialize the Thesis client with your API key:

```python
from thesis_py import Thesis

# Initialize client with API key
thesis = Thesis(api_key="your-api-key")

# Optional: specify custom base URL
thesis = Thesis(api_key="your-api-key", base_url="https://custom-endpoint.com")
```

## API Features

### Conversations

Create and manage AI-powered conversations with different research modes.

#### Create a New Conversation

```python
from thesis_py.api_schema import CreateNewConversationIntegrationRequest, ResearchMode

# Create a conversation with deep research mode
response = thesis.create_conversation(
    CreateNewConversationIntegrationRequest(
        initial_user_msg="What's the new DeFi meta recently that I can ape in?",
        research_mode=ResearchMode.DEEP_RESEARCH,
        system_prompt="You are a DeFi gigachad who's always ahead of the new DeFi meta.",
        space_id=123,  # Optional: link to a specific space
        space_section_id=456,  # Optional: link to a specific section
    )
)
print(f"Conversation ID: {response.conversation_id}")
```

#### Research Modes

- `ResearchMode.CHAT` - Interactive chat mode
- `ResearchMode.DEEP_RESEARCH` - Comprehensive research with citations
- `ResearchMode.FOLLOW_UP` - Follow-up research on existing topics

#### Get Conversation Details

```python
# Retrieve conversation by ID
conversation = thesis.get_conversation_by_id("conv_abc123def456")
print(f"Status: {conversation.status}")
print(f"Events: {len(conversation.events) if conversation.events else 0}")

# Async version
conversation = await thesis.get_conversation_by_id_async("conv_abc123def456")
```

#### Join Existing Conversation (Streaming)

```python
import asyncio
from thesis_py.api_schema import JoinConversationIntegrationRequest

async def join_conversation_example():
    async for event in thesis.join_conversation(
        JoinConversationIntegrationRequest(
            conversation_id="conv_abc123def456",
            user_prompt="Continue the research on recent DeFi trends",
            research_mode=ResearchMode.CHAT,
        )
    ):
        # Process streaming events
        print(f"Event: {event}")

# Run the async function
asyncio.run(join_conversation_example())
```

### Spaces

Manage research spaces and their sections.

#### List Spaces

```python
# Get all spaces with pagination
spaces = thesis.get_spaces(limit=10, offset=0)
print(f"Found {len(spaces.data)} spaces")

for space_item in spaces.data:
    space = space_item.space
    print(f"Space: {space.title} (ID: {space.id})")
```

#### Get Space Details

```python
# Get detailed information about a space
space_detail = thesis.get_space_by_id("868")
space = space_detail.data

print(f"Title: {space.title}")
print(f"Description: {space.description}")
print(f"Members: {space.memberCount}")
print(f"Research Count: {space.totalResearch}")
```

#### Get Space Sections

```python
# Get all sections within a space
sections = thesis.get_space_sections("868")

for section in sections.data:
    print(f"Section: {section.name}")
    print(f"Description: {section.description}")
    print(f"Output Type: {section.outputType}")
```

## Advanced Usage

### Working with Events

Process conversation events and extract structured data:

```python
from thesis_py.research.events import from_raw_events_to_pairs
from thesis_py.research.events.utils import get_pairs_from_events

# Get conversation and process events
conversation = thesis.get_conversation_by_id("conv_id")
pairs = from_raw_events_to_pairs(conversation.events[:2])

# For streaming events
async for event in thesis.join_conversation(request):
    pairs = get_pairs_from_events([event])
    print(pairs)
```

### Environment Variables

Set your API key using environment variables:

```bash
export THESIS_API_KEY="your-api-key-here"
export THESIS_BASE_URL="https://app-be.thesis.io"  # Optional
```

```python
import os
from thesis_py import Thesis

# Will automatically use THESIS_API_KEY from environment
thesis = Thesis(api_key=os.environ["THESIS_API_KEY"])
```

## Examples

Complete examples are available in the `examples/` directory:

- `hello_world.py` - Basic conversation creation
- `get_conversation.py` - Retrieve and process conversation events
- `get_spaces.py` - List and explore spaces
- `join_conversation.py` - Join conversations with streaming

## Error Handling

```python
import requests
from thesis_py import Thesis

try:
    thesis = Thesis(api_key="your-api-key")
    response = thesis.create_conversation(request)
except requests.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
    print(f"Response: {e.response.text}")
except ValueError as e:
    print(f"Validation Error: {e}")
```

## Data Models

The SDK uses Pydantic models for type safety and validation. Key models include:

- `ConversationCreateResponse` - Response from conversation creation
- `ConversationDetailResponse` - Detailed conversation information
- `SpaceListResponse` - List of spaces with pagination
- `SpaceDetailResponse` - Detailed space information
- `CreateNewConversationIntegrationRequest` - Request to create conversations
- `JoinConversationIntegrationRequest` - Request to join conversations

## Requirements

- Python 3.8+
- `httpx` for async HTTP requests
- `requests` for synchronous HTTP requests
- `pydantic` for data validation and serialization
