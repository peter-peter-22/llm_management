from pydantic import BaseModel

from src.interface2.tools.tool_handler import ToolRegistry, Tool


class GetWeatherArgs(BaseModel):
    location: str
    units: str = "celsius"


def get_weather(args) -> str:
    if not args:
        raise Exception("No arguments provided")
    location, units = GetWeatherArgs.model_validate(args).model_dump()
    # Mock implementation
    return f"The weather in {location}: {20 if units == "celsius" else 70}°{units}"


tool_name = "get_weather"
args_schema = {
    "type": "object",
    "properties": {
        "location": {
            "type": "string",
            "description": "City and country e.g. Bogotá, Colombia"
        },
        "units": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "description": "Units the temperature will be returned in."
        }
    },
    "required": ["location", "units"],
    "additionalProperties": False
}
args_json = '{"location": "Paris", "unit": "celsius"}'

t = ToolRegistry([
    Tool(
        get_weather,
        tool_name,
        "Retrieves current weather for the given location.",
        args_schema
    )
])

print("Normal", t.use_tool(tool_name, args_json))
print("No args", t.use_tool(tool_name))
print("Wrong tool", t.use_tool("test"))
print("Wrong args", t.use_tool(tool_name, '{"test": "Paris"}'))  # The breaks are escaped, this might be an issue
print("Invalid json", t.use_tool(tool_name, 'not a json'))
