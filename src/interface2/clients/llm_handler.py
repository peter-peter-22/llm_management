from typing import Any
from typing import Callable


class ToolCall:
    def __init__(
            self,
            function_name: str,
            arguments: str | dict[str, Any] | None = None
    ):
        self.function_name = function_name
        self.arguments = arguments


class AiResponse:
    def __init__(self, message: dict[str, Any], content: str, is_tool_call: bool = False,
                 tool_calls: list[ToolCall] | None = None):
        self.message = message
        self.content = content
        self.is_tool_call = is_tool_call
        self.tool_calls = tool_calls


class LlmHandler:
    def __init__(
            self,
            tools: list[Callable[..., Any]] | None = None,
            tool_choice: str | dict[str, Any] | None = None,
    ):
        self.tools = tools
        self.tool_choice = tool_choice

    def chat(self, messages: list[dict[str, Any]], *kwargs) -> AiResponse:
        pass
