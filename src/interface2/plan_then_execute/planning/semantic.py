from src.interface2.clients.ollama_qwen_llm import OllamaModel

llm = OllamaModel(model="qwen2.5:3b", model_args={"temperature": 0})

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


def plan_text(message: str):
    messages = [
        {"role": "system", "content": planner_system_prompt},
        {"role": "user", "content": message}
    ]
    plan_semantic = llm.chat(messages)
    return plan_semantic


def _test():
    res = plan_text("List the 3 most recent projects of the company, briefly describe their goal.")
    print(res.content)


if __name__ == "__main__":
    _test()
