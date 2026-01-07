import json
from typing import Callable, Any

from pydantic import BaseModel, ValidationError


class Tool:
    def __init__(self, func: Callable[..., Any], args_model: type[BaseModel] | None):
        self.args_model = args_model
        self.func = func


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


class GetWeatherArgs(BaseModel):
    location: str
    unit: str = "celsius"


def get_weather(location: str, unit: str = "celsius") -> str:
    # Mock implementation
    return f"Weather in {location}: 72° {unit}"


tool_name = "get_weather"
arguments_json = '{"location": "Paris", "unit": "celsius"}'

t = ToolRegistry({tool_name: Tool(get_weather, GetWeatherArgs)})

print(t.use_tool(tool_name, arguments_json))

try:
    t.use_tool(tool_name)
except Exception as e:
    print(f"No args: {e}")

try:
    t.use_tool("test")
except Exception as e:
    print(f"Wrong name: {e}")

try:
    t.use_tool(tool_name, '{"test": "Paris"}')
except Exception as e:
    print(f"Invalid args: {e}")
