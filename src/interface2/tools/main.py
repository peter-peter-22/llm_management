from pydantic import BaseModel

from src.interface2.clients.ollama_qwen_llm import OllamaQwen
from src.interface2.tools.tool_handler import ToolRegistry, Tool
from src.interface2.tools.tool_loop import ToolLoop


class GetTempArgs(BaseModel):
    units: str = "celsius"


def get_current_temperature(args) -> str:
    if not args:
        raise Exception("No arguments provided")
    test = GetTempArgs.model_validate(args).model_dump()
    units = test.get("units")
    return f"{20 if units == "celsius" else 70}°{units}"


tools = ToolRegistry([
    Tool(
        get_current_temperature,
        "get_current_temperature",
        """Get the current temperature at the user\'s location.""",
        {
            "type": "object",
            "properties": {
                "name": {
                    'type': ["celsius", "fahrenheit"],
                    'description': 'The unit of measurement.',
                    'default': 'celsius',
                }
            },
            'required': ["unit"]
        }
    )
])

llm = OllamaQwen(model="qwen2.5:3b", tool_choice="auto", tools=tools.describe_tools(), model_config={"temperature": 0})

messages = [
    {"role": "system", "content": "You are a helpful assistant. Do no make-up data, use tools when necessary."},
    {"role": "user", "content": "Tell me the current temperature in celsius."}
]

loop = ToolLoop(llm, tools, 1)
res = loop.loop(messages)

print(res.content)
