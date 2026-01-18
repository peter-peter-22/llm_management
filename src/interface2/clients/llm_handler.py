from typing import Any, Callable, TypeVar, Generic, Optional

from pydantic import BaseModel


class ToolCall:
    def __init__(
            self,
            function_name: str,
            arguments: str | dict[str, Any] | None = None
    ):
        self.function_name = function_name
        self.arguments = arguments


StructuredT = TypeVar("StructuredT", bound=BaseModel)


class AiResponse(Generic[StructuredT]):
    def __init__(
            self,
            message: dict[str, Any],
            content: str,
            is_tool_call: bool = False,
            tool_calls: list[ToolCall] | None = None,
            structured_response: Optional[StructuredT] = None,
    ):
        self.message = message
        self.content = content
        self.is_tool_call = is_tool_call
        self.tool_calls = tool_calls
        self.structured_response = structured_response


class LlmHandler:
    def __init__(
            self,
            model_args: dict[str, Any] | None = None,
    ):
        self.model_args = model_args

    def chat(
            self,
            messages: list[dict[str, Any]],
            tools: list[Callable[..., Any]] | None = None,
            tool_choice: str | dict[str, Any] | None = None,
            model_args: dict[str, Any] | None = None,
    ) -> AiResponse:
        pass
