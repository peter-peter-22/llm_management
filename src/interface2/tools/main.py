from typing import Literal

from pydantic import Field, BaseModel, validate_call

from src.interface2.clients.ollama_qwen_llm import OllamaQwen
from src.interface2.tools.tool_handler import Tool
from src.interface2.tools.tool_loop import ToolLoop


class GetTemperatureArgs(BaseModel):
    units: Literal["celsius", "fahrenheit"] = Field(description="The unit of measurement.", default="celsius")


@validate_call
def get_current_temperature(args: GetTemperatureArgs) -> str:
    units = args.units
    return f"{20 if units == "celsius" else 70}°{units}"


tools = [
    Tool(
        get_current_temperature,
        "get_current_temperature",
        """Get the current temperature at the user\'s location.""",
        GetTemperatureArgs
    )
]

llm = OllamaQwen(model="qwen2.5:3b", model_args={"temperature": 0})

messages = [
    {"role": "system", "content": "You are a helpful assistant. Do no make-up data, use tools when necessary."},
    {"role": "user", "content": "Tell me the current temperature in celsius."}
]

loop = ToolLoop(llm, tools, model_args={"tool_choice": "auto"})
res = loop.loop(messages)

print(res.content)
