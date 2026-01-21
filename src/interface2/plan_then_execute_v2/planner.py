from typing import Literal

from pydantic import BaseModel, Field

from src.interface2.clients.ollama_qwen_llm import OllamaModel
from src.interface2.tools.tool_loop import ToolLoop

llm = OllamaModel(
    model="qwen2.5:7b-instruct",
    model_args={
        "temperature": 0,
        "top_p": 0.9,
        "top_k": 40
        # "response_format": {"type": "json_object"}
    }
)

planner_system_prompt = """
You are a planner.
Output a JSON plan using the response tool.
Use only known capabilities and business concepts.
Do not invent schema or SQL.
If an input is unknown, use "__UNKNOWN__".
Reference step outputs symbolically.


AVAILABLE CAPABILITIES

[DB_SCHEMA]
Inputs:
- scope: projects | employees
Outputs:
- entity_fields
Guarantees:
- Complete and current

[DB_QUERY]
Inputs:
- sql
Outputs:
- rows
Guarantees:
- Text fields are RAW

[SUMMARIZE]
Inputs:
- text, max_length
Outputs:
- summary
"""


class Step(BaseModel):
    id: int
    capability: Literal["DB_SCHEMA", "DB_QUERY", "SUMMARIZE"]
    inputs: dict[str, str] = Field(
        description="Include the inputs of the capability here. To reference outputs of a step, use:'<step_id>.<output_field>'")
    status: Literal["pending", "blocked"] = Field(description="Blocked if depends on still unknown data")


class Plan(BaseModel):
    steps: list[Step]


agent = ToolLoop[Plan](llm, response_model=Plan, tool_choice="required")


def create_plan(message: str):
    messages = [
        {"role": "system", "content": planner_system_prompt},
        {"role": "user", "content": message}
    ]
    plan = agent.loop(messages).structured_response
    return plan


def _test():
    res = create_plan("List the 3 most recent projects of the company, briefly describe their goal.")
    print(res)


if __name__ == "__main__":
    _test()
