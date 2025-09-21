from pydantic import BaseModel, Field, field_serializer

from thesis_py.research.events.schema.research import ResearchMode

# Response Models
class ConversationCreateResponse(BaseModel):
    status: str = Field(
        description="Response status, always 'ok' for successful creation", example='ok'
    )
    conversation_id: str = Field(
        description='Unique identifier for the created conversation',
        example='conv_abc123def456',
    )

class ConversationEvent(BaseModel):
    action: str = Field(description='Type of action/event', example='message')
    source: str = Field(description='Source of the event (user/agent)', example='user')
    message: str = Field(
        description='Content of the message or action',
        example='Please review this code',
    )
    timestamp: str = Field(
        description='ISO timestamp when the event occurred',
        example='2024-01-15T10:30:00Z',
    )


class ConversationDetailResponse(BaseModel):
    conversation_id: str = Field(
        description='Unique conversation identifier', example='conv_abc123def456'
    )
    title: str = Field(description='Conversation title', example='Code Review Session')
    status: str = Field(description='Current conversation status', example='RUNNING')
    created_at: str = Field(
        description='ISO timestamp when conversation was created',
        example='2024-01-15T10:30:00Z',
    )
    last_updated_at: str = Field(
        description='ISO timestamp of last activity', example='2024-01-15T11:45:00Z'
    )
    selected_repository: str | None = Field(
        description='Associated repository if any', example='user/project-repo'
    )
    research_mode: str | None = Field(
        description='Research mode used in conversation', example='deep_research'
    )
    events: list[dict] | None = Field(
        description='List of conversation events/messages', default=None
    )
    final_result: str | dict | None = Field(
        description='Final result if conversation is completed', default=None
    )
    
class CreateNewConversationIntegrationRequest(BaseModel):
    initial_user_msg: str | None = Field(
        None,
        description='Initial message to start the conversation',
        example="What's the new DeFi meta recently that I can ape in?",
    )
    research_mode: ResearchMode | None = Field(
        None, description='Research mode for the conversation', example='deep_research'
    )
    space_id: int | None = Field(
        None,
        description='Your space ID. You can find it via your created space',
        example=123,
    )
    space_section_id: int | None = Field(
        None,
        description='Your space section ID. You can find it via your created space',
        example=456,
    )
    thread_follow_up: int | None = Field(
        None, description='Thread ID for follow-up conversations', example=789
    )
    followup_discover_id: str | None = Field(
        None,
        description='Discovery ID for follow-up research',
        example='discover_abc123',
    )
    mcp_disable: dict[str, bool] | None = Field(
        None,
        description='MCP tools to disable for this conversation',
    )
    system_prompt: str | None = Field(
        None,
        description='Custom system prompt to guide the AI behavior',
        example="You are a DeFi gigachad who's always ahead of the new DeFi meta.",
    )
    
    @field_serializer("research_mode")
    def serialize_research_mode(self, research_mode: ResearchMode | None, _info) -> str | None:
        return research_mode.value if research_mode else None

class CreateChatConversationIntegrationRequest(BaseModel):
    initial_user_msg: str | None = Field(
        None,
        description='Initial message for the chat conversation',
        example="Let's have a casual conversation about DeFi",
    )
    system_prompt: str | None = Field(
        None,
        description="System prompt to set the AI's behavior in chat mode",
        example='You are a friendly AI assistant who explains complex topics simply',
    )


class CreateDeepResearchConversationIntegrationRequest(BaseModel):
    initial_user_msg: str | None = Field(
        None,
        description='Initial research query to begin deep analysis',
        example='Research the latest developments in DeFi',
    )
    mcp_disable: dict[str, bool] | None = Field(
        None,
        description='MCP tools to disable during deep research',
    )
    system_prompt: str | None = Field(
        None,
        description='System prompt for deep research mode behavior',
        example='You are a thorough DeFi researcher who provides comprehensive analysis with citations',
    )

class JoinConversationIntegrationRequest(BaseModel):
    conversation_id: str | None = Field(
        None,
        description='ID of the existing conversation to join',
        example='conv_abc123def456',
    )
    user_prompt: str | None = Field(
        None,
        description='Message to send when joining the conversation',
        example='Please review the code we discussed earlier',
    )
    research_mode: ResearchMode | None = Field(
        None,
        description='Research mode to use in the conversation. Must be one of: chat, deep_research, follow_up',
        example=ResearchMode.DEEP_RESEARCH.value,
    )
    latest_event_id: int | None = Field(
        None,
        description='ID of the latest event to resume from',
        example=123,
    )
    x_device_id: str | None = Field(
        None,
        description='Device ID to use for the conversation',
        example='123',
    )

    @field_serializer("research_mode")
    def serialize_research_mode(self, research_mode: ResearchMode | None, _info) -> str | None:
        return research_mode.value if research_mode else None