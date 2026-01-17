import json
from typing import Callable, Any

from pydantic import BaseModel


class Tool:
    def __init__(
            self,
            func: Callable[..., str],
            name: str,
            description: str | None = None,
            parameters: dict[str, Any] | None = None,
            strict: bool = True,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func
        self.strict = strict


def describe_args(args_model: type[BaseModel]) -> dict[str, Any]:
    return args_model.model_json_schema()


def describe_tool(tool: Tool):
    tool_definition: dict[str, str | dict[str, Any]] = {
        "type": "function",
        "function": {  # This field different from the OpenAI standard. Ollama doesn't accept that format.
            "name": tool.name,
            "description": tool.description,
            "strict": tool.strict
        }
    }
    if tool.parameters:
        tool_definition["function"]["parameters"] = tool.parameters
    return tool_definition


def format_tool_response(tool_name: str, res: str):
    return {
        "role": "tool",
        "tool_name": tool_name,
        "content": res
    }


def format_error_response(tool_name: str, message: str):
    return {
        "role": "tool",
        "tool_name": tool_name,
        "content": json.dumps({
            "ok": False,
            "error": message,
        })
    }


class ToolRegistry:
    tools: dict[str, Tool]

    def __init__(self, tools: list[Tool]):
        self.tools = {tool.name: tool for tool in tools}

    def use_tool(self, name: str, args: str | dict[str, Any] | None = None):
        # Get the tool
        try:
            tool = self.tools[name]
        except KeyError:
            return format_error_response(name, f"Unknown tool: {name}"), True

        # Parse the args
        args_dict: dict[str, Any] | None = None
        try:
            if args is not None:
                if isinstance(args, str):
                    args_dict = json.loads(args)
                else:
                    args_dict = args
        except json.JSONDecodeError as e:
            return format_error_response(name, f"Invalid JSON in arguments: {e}"), True

        # Call the tool
        error = False
        try:
            content = tool.func(args_dict)
        except Exception as e:
            content = json.dumps({
                "ok": False,
                "error": str(e),
            })
            error = True

        # Build the response
        return format_tool_response(tool.name, content), error

    def describe_tools(self):
        tool_definitions = []
        for tool in self.tools.values():
            tool_definitions.append(describe_tool(tool))
        print(json.dumps(tool_definitions, indent=2))
        return tool_definitions
