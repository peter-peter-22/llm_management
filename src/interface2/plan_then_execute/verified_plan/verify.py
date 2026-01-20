from typing import Literal

from pydantic import BaseModel, Field

from src.interface2.clients.ollama_qwen_llm import OllamaModel
from src.interface2.tools.tool_loop import ToolLoop

llm = OllamaModel(model="qwen2.5:3b", model_args={"temperature": 0})

system_prompt = """Your job is to check if the provided plan appears to be correct and logical based on the given goal and requirements.
Check only if the plan follows a sane logic, do not go into the details.
Your response must answer if plans seems correct or not.
If incorrect, decide if it can be fixed with minor changes or it needs a full rebuild.
If fixable, describe what steps need to be modified, added or removed in the instructions field.
The goal of the changes is to make the plan to fulfill the listed requirements.
Always respond with the response tool.
"""


class Rating(BaseModel):
    rating: Literal["valid", "fixable", "rebuild"] = Field(description="", default="valid")
    instructions: str = Field(description="Instructions about fixing or rebuilding if necessary.", default="")


agent = ToolLoop[Rating](llm, response_model=Rating, tool_choice="required")

baseline_requirements = [
    "Do not query the database to retrieve all record, always use filters or limits."
]


def verify_plan(goal: str, plan_steps: list[str], requirements: list[str]):
    plan_text = "The steps:\n" + "\n".join([f"{i + 1}: {step}" for i, step in enumerate(plan_steps)])
    requirements_text = f"The goal:\n{goal}"
    requirements_text += "\nRequirements:\n" + "\n".join([f"-{req}\n" for req in requirements + baseline_requirements])
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": plan_text},
        {"role": "user", "content": requirements_text}
    ]
    res = agent.loop(messages)
    return res.structured_response


def _test():
    goal = "List the 3 most recent projects of the company, briefly describe their goal."
    steps = [
        'Query the SQL database of Fakesoft for a list of all projects with their respective completion dates and sort them in descending order by completion date to identify the 3 most recent projects.',
        'Present the results from step 1 to a text transformation agent for semantic processing, converting the project descriptions into concise briefs that highlight the main goal or objective of each project.',
        'After receiving the processed briefs from the text transformation agent, present the list of the 3 most recent projects and their brief descriptions to the user as the final answer.'
    ]
    reqs = [
        'Identify the 3 most recent projects of the company.',
        'Briefly describe the goal of each project.'
    ]
    res = verify_plan(goal, steps, reqs)
    print("Correct", res)

    wrong_steps = [
        'Query the SQL database of Fakesoft for a list of all projects',
        'Present the results from step 1 to a text transformation agent for semantic processing, converting the project descriptions into concise briefs that highlight the main goal or objective of each project.',
        'After receiving the processed briefs from the text transformation agent, present the list of the 3 most recent projects and their brief descriptions to the user as the final answer.'
    ]

    res = verify_plan(goal, wrong_steps, reqs)
    print("Incorrect", res)


if __name__ == "__main__":
    _test()
