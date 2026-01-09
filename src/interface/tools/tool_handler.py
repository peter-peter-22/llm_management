import json
from typing import Callable, Any

from pydantic import BaseModel, ValidationError


class Tool:
    def __init__(
            self,
            func: Callable[..., Any],
            args_model: type[BaseModel] | None = None,
            required: list[str] | None = None,
            strict: bool = True
    ):
        self.args_model = args_model
        self.func = func
        self.required = required
        self.strict = strict
        self.strict = strict


def describe_tool(name: str, tool: Tool):
    args_schema = tool.args_model.model_json_schema() if tool.args_model else None

    # To mimic a full OpenAI tool definition (optional, for debugging)
    tool_definition = {
        "type": "function",
        "function": {
            "name": name,
            "description": tool.func.__doc__,
            "parameters": args_schema,
            "strict": True
        },
        "required": ["location"]
    }
    return tool_definition


class ToolRegistry:
    tools: dict[str, Tool]

    def __init__(self, tools: dict[str, Tool]):
        self.tools = tools

    def use_tool(self, name: str, args: str | None = None):
        # Get the tool
        try:
            tool = self.tools[name]
        except KeyError:
            raise KeyError(f"Unknown tool: {name}")

        # Parse the args
        args_dict: dict[str, str] | None = None
        try:
            if args is not None and args != "":
                args_dict = json.loads(args)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in arguments: {e}")

        # Validate the args
        if tool.args_model:
            try:
                if args_dict is None:
                    raise ValueError(f"No arguments provided but the function requires it.")
                validated_args = tool.args_model.model_validate(args_dict)
                args_dict = validated_args.model_dump()  # Convert back to dict for **kwargs
                print(args_dict)
            except ValidationError as e:
                # Needs better validation
                raise ValueError(f"Argument validation failed: {e}")

    def describe_tools(self):
        tool_definitions = []
        for name, tool in self.tools.items():
            tool_definitions.append(describe_tool(name, tool))
        print(json.dumps(tool_definitions, indent=2))
        return tool_definitions
