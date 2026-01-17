import json

from litellm.types.utils import ModelResponse
from ollama import chat
from pydantic import BaseModel, Field

"""
openai docs about tools calling:
https://platform.openai.com/docs/guides/function-calling
"""


class GetWeather(BaseModel):
    """Get the current weather at a location."""
    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: str = Field("celsius", description="Temperature unit: celsius or fahrenheit")


# Inspect the raw JSON schema (this is what Instructor sends as 'parameters')
schema = GetWeather.model_json_schema()
print(json.dumps(schema, indent=2))

# To mimic a full OpenAI tool definition (optional, for debugging)
tool_definition = {
    "type": "function",
    "function": {
        "name": GetWeather.__name__.lower(),  # Instructor typically uses class name
        "description": GetWeather.__doc__,
        "parameters": schema,
        "strict": True  # If using strict mode
    },
    "required": ["location"]
}
print(json.dumps(tool_definition, indent=2))


def execute_tool_calls(response: ModelResponse):
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.model_extra.get("type") != "function":
            continue

        func = tool_call.model_extra.get("function")
        name = func.name
        args = json.loads(func.arguments)

        print(name)
        print(args)

    #     result = call_function(name, args)
    #     input_messages.append({
    #         "type": "function_call_output",
    #         "call_id": tool_call.call_id,
    #         "output": str(result)
    #     })
    # return tool_messages


def chat_with_tools(message: str, max_iterations: int = 10) -> str:
    response: ModelResponse = chat(
        model="qwen2.5:3b",
        options={
            "temperature": 0,
            "tool_choice": "auto"
        },
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Do no make-up data, use tools when necessary."},
            {"role": "user", "content": message}
        ],
        tools=[tool_definition]
    )
    print(response)
    execute_tool_calls(response)


print(chat_with_tools("What is the current weather and temperature in celsius at New York?"))
