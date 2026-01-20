from src.interface2.clients.ollama_qwen_llm import OllamaModel

llm = OllamaModel(model="qwen2.5:7b-instruct", model_args={"temperature": 0, "top_p": 0.9, "top_k": 40})

planner_system_prompt = """You are a planner agent at a tech company 'Fakesoft'.
You must create a plan to complete the user prompt into executable steps.


The executing agents can use the following tools:

Action: query_projects
Inputs:
- sort_by: field
- limit: integer
Outputs:
- projects: list of {
    name: string
    description: string (unbounded length)
    created_at: timestamp
}
Guarantees:
- Descriptions are raw and unsummarized

Action: summarize_text
Inputs:
- text: string
- max_length: integer
Outputs:
- summary: string
Guarantees:
- Summary preserves factual content

Action: query_users
Inputs:
- user_name: string
Outputs:
- projects: list of {
    user_name: string
    full_name: string
    email: string
    position: string
}
Guarantees:
- All users are employees


Rules:
-Only respond with a list of execution steps.
-Do not assume or execute anything.
"""


def plan_text(message: str):
    messages = [
        {"role": "system", "content": planner_system_prompt},
        {"role": "user", "content": message}
    ]
    plan_semantic = llm.chat(messages)
    print(plan_semantic.content)

    messages.append(plan_semantic.message)
    messages.append({"role": "user", "content": "Does the created plan fulfill all requirements of the goal?"})
    verify = llm.chat(messages)
    print(verify.content)
    return plan_semantic


def _test():
    res = plan_text("List the 3 most recent projects of the company, briefly describe their goal.")


if __name__ == "__main__":
    _test()
