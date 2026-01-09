from typing import Protocol, Callable
from typing import TypedDict, NotRequired, Any, Union


class ToolCall:
    def __init__(
            self,
            function_name: str,
            arguments: str,
            id: str
    ):
        self.function_name = function_name
        self.arguments = arguments
        self.id = id


class FormattedChatMessage:
    def __init__(self, message, tool_calls: list[ToolCall] | None, is_tool_call: bool):
        self.message = message
        self.tool_calls = tool_calls
        self.is_tool_call = is_tool_call


class ChatMessageTyped(TypedDict):
    role: str
    content: str
    original: NotRequired[Any]
    text: NotRequired[str]
    tool_calls: NotRequired[list[ToolCall]]
    is_tool_call: NotRequired[bool]
    id: NotRequired[str]


type ChatMessage = Union[ChatMessageTyped, dict[str, Any]]


class ProcessChat(Protocol):
    def __call__(self, messages: list[ChatMessage], *kwargs) -> ChatMessage: ...


class LlmHandler:
    def __init__(
            self,
            chat: ProcessChat,
            tools: list[Callable[..., Any]] | None = None,
            tool_choice: str | dict[str, Any] | None = None,
    ):
        self.chat = chat
        self.tools = tools
        self.tool_choice = tool_choice
