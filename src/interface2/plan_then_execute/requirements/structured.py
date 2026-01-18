import json

from pydantic import BaseModel, Field

from src.interface2.clients.ollama_qwen_llm import OllamaModel
from src.interface2.tools.tool_loop import ToolLoop

llm = OllamaModel(model="qwen2.5:3b", model_args={"temperature": 0})

system_prompt = """Format the provided requirement list with the response tool."""


class Requirements(BaseModel):
    requirements: list[str] = Field(description="List of requirements.")


agent = ToolLoop[Requirements](llm, response_model=Requirements, tool_choice="required")


def requirements_structured(message: str):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    requirements = agent.loop(messages)
    return requirements.structured_response


def _test():
    res = requirements_structured("""Requirements:
    1. Identify the 3 most recent projects of the company.
    2. Briefly describe the goal of each project.""")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    _test()
