from src.interface2.clients.ollama_qwen_llm import OllamaModel

llm = OllamaModel(model="qwen2.5:3b", model_args={"temperature": 0, "top_p": 0.9, "top_k": 40})

planner_system_prompt = """You are AI agent at a tech company 'Fakesoft', often referred to as 'company' or 'us'.
Your job is to design a list of constraints those must be fulfilled in during the completion of the user prompt.
Do not think about data or execution, base the constrains only on the user prompt.
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
