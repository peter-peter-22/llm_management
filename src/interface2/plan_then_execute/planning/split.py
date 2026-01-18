from pydantic import BaseModel, Field

from src.interface2.clients.ollama_qwen_llm import OllamaModel
from src.interface2.tools.tool_loop import ToolLoop

llm = OllamaModel(model="qwen2.5:3b", model_args={"temperature": 0})

system_prompt = """You will be provided with a list of the steps of a plan.
Use the response tool to format them."""


class PlanSteps(BaseModel):
    steps: list[str] = Field(description="List of the steps")


agent = ToolLoop[PlanSteps](llm, response_model=PlanSteps, tool_choice="required")


def plan_split(message: str):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    requirements = agent.loop(messages)
    return requirements.structured_response


def _test():
    res = plan_split("""1. Query the SQL database of Fakesoft for a list of all projects with their respective completion dates and sort them in descending order by completion date to identify the 3 most recent projects.
2. Present the results from step 1 to a text transformation agent for semantic processing, converting the project descriptions into concise briefs that highlight the main goal or objective of each project.
3. After receiving the processed briefs from the text transformation agent, present the list of the 3 most recent projects and their brief descriptions to the user as the final answer.""")
    print(res)


if __name__ == "__main__":
    _test()
