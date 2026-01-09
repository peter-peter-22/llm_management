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
