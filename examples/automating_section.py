import os
from thesis_py import Thesis
from thesis_py.api_schema import CreateNewConversationIntegrationRequest, ResearchMode
from thesis_py.research.events import from_raw_events_to_pairs
from time import sleep

from thesis_py.research.events.action.agent import AgentFinishAction
from thesis_py.research.events.schema.action import ActionType
from thesis_py.research.events.schema.agent import AgentState
from thesis_py.research.events.observation.agent import AgentStateChangedObservation

THESIS_API_KEY = os.environ.get("THESIS_API_KEY")

if not THESIS_API_KEY:
    raise ValueError("THESIS_API_KEY environment variable not set!")

thesis = Thesis(THESIS_API_KEY)


def main():
    response = thesis.create_conversation(
        CreateNewConversationIntegrationRequest(
            initial_user_msg="What's the new DeFi meta recently that I can ape in? Give me detailed info about Project name, project description, CEOs, backers, current X mindshare percentage, main project token, current token price, price change within 30 days. Give me 5 projects that have at least 100% price change within 30 days.",
            research_mode=ResearchMode.DEEP_RESEARCH,
            space_id=int(os.environ.get("THESIS_SPACE_ID")),
            space_section_id=int(os.environ.get("THESIS_SPACE_SECTION_ID")),
            mcp_disable={
                "hyperwhales": True,
                "liquidity": True,
                "stable": True,
                "browser_mcp": True,
                "investing_news": True,
                "jina": True,
                "arbitraging": True,
                "netlify": True,
                "meme": True,
                "perpetual_whales_analysis": True,
                "defi_earn": True,
                "token_metrics": True,
            },
        )
    )

    print(response.conversation_id)

    print("Waiting for Thesis.io to finish the conversation...")
    last_printed_index = -1

    while True:
        finished = False
        response = thesis.get_conversation_by_id(response.conversation_id)
        events = from_raw_events_to_pairs(response.events)

        # Print new events from last_printed_index + 1 onward
        new_events = events[last_printed_index + 1 :]
        if new_events:
            print()
            print("-" * 50)
            print()
            for event in new_events:
                print(event)
            last_printed_index = len(events) - 1

        # Check for finished state
        for event in reversed(events):
            if isinstance(event[1], AgentStateChangedObservation) and (
                event[1].agent_state == AgentState.FINISHED
                or event[1].agent_state == AgentState.AWAITING_USER_INPUT
            ):
                finished = True
                break
            if isinstance(event[0], AgentFinishAction) and event[0].task_completed:
                finished = True
                break
            if event[0].action == ActionType.FINISH and event[0].task_completed:
                finished = True
                break
        if finished:
            break
        sleep(5)


if __name__ == "__main__":
    main()
