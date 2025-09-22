import os
import asyncio
from thesis_py import Thesis
from thesis_py.api_schema import JoinConversationIntegrationRequest, ResearchMode
from thesis_py.research.events.utils import get_pairs_from_events

THESIS_API_KEY = os.environ.get("THESIS_API_KEY")

if not THESIS_API_KEY:
    raise ValueError("THESIS_API_KEY environment variable not set!")


async def main():
    thesis = Thesis(THESIS_API_KEY)

    async for event in thesis.join_conversation(
        JoinConversationIntegrationRequest(
            conversation_id="b3052a322b5b4149a4c46a02584e2dbb",
            user_prompt="What's the new DeFi meta recently that I can ape in?",
            research_mode=ResearchMode.CHAT,
        )
    ):
        pairs = get_pairs_from_events([event])
        print(pairs)


if __name__ == "__main__":
    asyncio.run(main())
