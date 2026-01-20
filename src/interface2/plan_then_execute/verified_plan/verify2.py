from pydantic import BaseModel, Field

from src.interface2.clients.ollama_qwen_llm import OllamaModel
from src.interface2.tools.tool_loop import ToolLoop

llm = OllamaModel(model="qwen2.5:3b", model_args={"temperature": 0, "top_p": 0.9, "top_k": 40})

system_prompt = """Your job is to check if the provided plan appears to be correct and logical based on the given requirements.

Rules:
-Check if the plan follows a correct logic and fulfills the requirements.
-Do not try to execute or assume anything.
-Your response must answer if the plan seems correct and list the missed requirements.
-Include the following in your answer: the validity of the plan (yes/no), the missing requirements (if any)
-Be concise.
"""

planner_system_prompt = """You are a planner agent at a tech company 'Fakesoft'.
You must create a plan to complete the user prompt into executable and verifiable steps.
At the end of the plan, include a step for presenting a final answer to the user.

The execution steps will be forwarded to agents with the following capabilities:
-Query the SQL database of Fakesoft for internal information with various filters and limits.
-Semantically transform texts.

Rules:
-Only respond with execution steps.
-Think with the capabilities of the executing agents.
-You must not invent data.
-In each step, include the required actions, the required output or effect, the required inputs.
"""


class Rating(BaseModel):
    valid: bool
    missed_requirements: str = Field(
        description="Briefly describe which parts of the requirements were missed.",
        default="")


agent = ToolLoop[Rating](llm, response_model=Rating, tool_choice="required")

baseline_requirements = [
    "Do not query the database to retrieve all records, always use filters or specify the max count."
]


def verify_plan(plan_steps: list[str], requirements: list[str]):
    plan_text = "The plan:\n" + "\n".join([f"{i + 1}: {step}" for i, step in enumerate(plan_steps)])
    requirements_text = "Check if the plan fulfills the following requirements:\n" + "\n".join(
        [f"-{req}" for req in requirements + baseline_requirements])
    goal = "List the 3 most recent projects of the company, briefly describe their goal."
    messages = [
        {"role": "system", "content": planner_system_prompt},
        {"role": "user", "content": goal},
        {"role": "assistant", "content": plan_text},
        {"role": "user", "content": requirements_text},
    ]
    res = llm.chat(messages)
    return res.content


def _test():
    steps = [
        'Query the SQL database of Fakesoft for a list of all projects with their respective completion dates and sort them in descending order by completion date to identify the 3 most recent projects.',
        'Present the results from step 1 to a text transformation agent for semantic processing, converting the project descriptions into concise briefs that highlight the main goal or objective of each project.',
        'After receiving the processed briefs from the text transformation agent, present the list of the 3 most recent projects and their brief descriptions to the user as the final answer.'
    ]
    reqs = [
        'Identify the 3 most recent projects of the company.',
        'Briefly describe the goal of each project.'
    ]
    res = verify_plan(steps, reqs)
    print("Correct", res)

    wrong_steps = [
        'Query the SQL database of Fakesoft for a list of all projects',
        'Present the results from step 1 to a text transformation agent for semantic processing, converting the project descriptions into concise briefs that highlight the main goal or objective of each project.',
        'After receiving the processed briefs from the text transformation agent, present the list of the 3 most recent projects and their brief descriptions to the user as the final answer.'
    ]

    res = verify_plan(wrong_steps, reqs)
    print("Incorrect", res)


if __name__ == "__main__":
    _test()
