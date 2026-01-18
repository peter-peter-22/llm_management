import json
from typing import Any, Type, TypeVar, Generic

from pydantic import BaseModel

from src.interface2.clients.llm_handler import LlmHandler, AiResponse
from src.interface2.tools.tool_handler import format_tool_response, format_error_response, Tool, ToolRegistry, \
    clean_schema

response_tool_name = "response_tool"

StructuredT = TypeVar("StructuredT", bound=BaseModel)


class ToolLoop(Generic[StructuredT]):
    def __init__(
            self,
            model: LlmHandler,
            tools: list[Tool] | None = None,
            retries: int = 1,
            max_steps: int = 5,
            model_args: dict[str, Any] | None = None,
            response_model: Type[StructuredT] | None = None,
    ):
        # Create the response tool for structured response if needed
        if response_model:
            def response_func(args):
                return response_model.model_validate(args)

            response_tool = Tool(
                response_func,
                response_tool_name,
                "Use this tool to format your response",
                clean_schema(response_model.model_json_schema()),
                True
            )
            if not tools:
                tools = [response_tool]
            else:
                tools.append(response_tool)

        self.model = model
        self.tools = tools
        self.retries = retries
        self.max_steps = max_steps
        self.model_args = model_args
        self.response_model = response_model
        self.tool_registry = ToolRegistry(tools)
        self.tool_json = self.tool_registry.describe_tools() if self.tool_registry else None

    def loop(self, messages: list[dict[str, Any]]) -> AiResponse | AiResponse[StructuredT]:
        remaining_retries = self.retries
        remaining_steps = self.max_steps
        while remaining_retries >= 0 and remaining_steps >= 0:
            res = self.model.chat(messages, tools=self.tool_json, **self.model_args if self.model_args else None)
            if res.is_tool_call:
                print(f"Executing {len(res.tool_calls)} tool call(s).")
                for tool_call in res.tool_calls:
                    # Call the tool
                    print(f"Function: {tool_call.function_name}, Args: {tool_call.arguments}")
                    (tool_res, error) = self.tool_registry.use_tool(tool_call.function_name, tool_call.arguments)
                    print("Tool res:", tool_res)

                    # Use the response tool when needed
                    if tool_call.function_name == response_tool_name and not error:
                        structured_res: StructuredT = tool_res
                        res.structured_response = structured_res
                        return res

                    # Use generic tools
                    content = tool_res if isinstance(tool_res, str) else json.dumps(tool_res, indent=2)
                    if not error:
                        messages.append(format_tool_response(tool_call.function_name, content))
                        remaining_retries = self.retries
                    else:
                        messages.append(format_error_response(tool_call.function_name, content))
                        remaining_retries -= 1

                    remaining_steps -= 1
            else:
                if self.response_model:  raise Exception("Got text instead of response tool call")
                return res
        raise Exception("No more retries left") if remaining_retries < 0 else Exception("Step limit exceeded")
