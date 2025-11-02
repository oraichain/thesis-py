import os
import asyncio
from thesis_py import Thesis
from thesis_py.api_schema import CreateNewConversationIntegrationRequest, ResearchMode
from thesis_py.api_schema.conversations import ListConversationIntegrationRequest
from thesis_py.research.events.utils import get_pairs_from_events

THESIS_API_KEY = os.environ.get("THESIS_API_KEY")

if not THESIS_API_KEY:
    raise ValueError("THESIS_API_KEY environment variable not set!")


async def main():
    thesis = Thesis(THESIS_API_KEY)

    conversation_response = await thesis.create_conversation_async(
        CreateNewConversationIntegrationRequest(
            initial_user_msg="What's the new DeFi meta recently that I can ape in?",
            research_mode=ResearchMode.DEEP_RESEARCH,
        )
    )

    async for event in thesis.listen_conversation(
        ListConversationIntegrationRequest(
            conversation_id=conversation_response.conversation_id,
        )
    ):
        pairs = get_pairs_from_events([event])
        print(pairs)


if __name__ == "__main__":
    asyncio.run(main())
