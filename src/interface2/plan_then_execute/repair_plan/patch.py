from typing import Literal, Union

from pydantic import BaseModel, Field

from src.interface2.clients.ollama_qwen_llm import OllamaModel
from src.interface2.tools.tool_loop import ToolLoop

llm = OllamaModel(model="qwen2.5:3b", model_args={"temperature": 0})

system_prompt = """Your job is to list the necessary operations about fixing a faulty plan based on the provided instructions.

Rules:
-Do not assume anything.
-Follow the instructions strictly.
-Respond the list of changes by using the response tool.
-Prioritize modification.
"""


class Edit(BaseModel):
    operation: Literal["modify", "replace"] = Field(default="modify")
    step_number: int = Field(description="The step to edit.")
    message: str = Field(description="Instructions about the necessary change or the new step.")


class Add(BaseModel):
    operation: Literal["insert_before", "insert_after"] = Field(
        description="How the new step should be inserted.")
    step_number: int = Field(description="Where the new step should be inserted.")
    message: str = Field(description="The message of the new step.")


class Remove(BaseModel):
    operation: Literal["remove"] = Field(default="remove")
    step_number: int = Field(description="The step to remove.")


class Repair(BaseModel):
    changes: list[Union[Add, Remove, Edit]] = Field(description="The list of changes in the plan.")


agent = ToolLoop[Repair](llm, response_model=Repair, tool_choice="required")


def repair_plan(instruction: str, plan_steps: list[str]):
    text = "The plan:\n" + "\n".join([f"{i + 1}: {step}" for i, step in enumerate(plan_steps)])
    text += "\n\nInstructions:\n" + instruction
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    res = agent.loop(messages)
    return res.structured_response


def _test():
    steps = [
        'Query the SQL database of Fakesoft for a list of all projects',
        'Present the results from step 1 to a text transformation agent for semantic processing, converting the project descriptions into concise briefs that highlight the main goal or objective of each project.',
        'After receiving the processed briefs from the text transformation agent, present the list of the 3 most recent projects and their brief descriptions to the user as the final answer.'
    ]
    instruction = "The steps need a minor modification. Step 1 should be removed as it does not align with the requirement to identify and list only the 3 most recent projects. Steps 2 and 3 remain unchanged."
    res = repair_plan(instruction, steps)
    print(res)


if __name__ == "__main__":
    _test()
