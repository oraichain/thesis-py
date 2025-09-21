from enum import Enum


class ObservationType(str, Enum):
    READ = 'read'
    """The content of a file
    """

    WRITE = 'write'

    EDIT = 'edit'

    RUN = 'run'
    """The output of a command
    """

    RUN_IPYTHON = 'run_ipython'
    """Runs a IPython cell.
    """

    CHAT = 'chat'
    """A message from the user
    """

    DELEGATE = 'delegate'
    """The result of a task delegated to another agent
    """

    MESSAGE = 'message'

    ERROR = 'error'

    SUCCESS = 'success'

    NULL = 'null'

    THINK = 'think'

    AGENT_STATE_CHANGED = 'agent_state_changed'

    USER_REJECTED = 'user_rejected'

    CONDENSE = 'condense'
    """Result of a condensation operation."""

    RECALL = 'recall'
    """Result of a recall operation. This can be the workspace context, a microagent, or other types of information."""

    MCP = 'mcp'
    """Result of a MCP Server operation"""

    BROWSER_MCP = 'browser_mcp'

    MCP_PLAN = 'mcp_plan'
    """Result of a MCP Plan operation. The response is a dict with the plan ID and the tasks."""

    PLAYWRIGHT_MCP_BROWSER_SCREENSHOT = 'playwright_mcp_browser_screenshot'
    """Result of a Playwright MCP Browser Screenshot operation. The response is a base64 encoded string of the screenshot, which should be streamed to the client using the correct format matching
    browsergym's screenshot format."""

    REPORT_VERIFICATION = 'report_verification'
    """Result of the evaluation pipeline verifying the generated report. The response is a boolean."""
    CREDIT_ERROR = 'credit_error'
    """Result of a credit check."""

    GET_CURRENT_DATE = 'get_current_date'
    """Result of a get current date operation."""
    AGENT_READY = 'agent_ready'
    """Emitted when agent has completed initialization and is ready to process actions."""
