from src.interface2.clients.ollama_qwen_llm import OllamaModel

llm = OllamaModel(model="qwen2.5:3b", model_args={"temperature": 0})

requirements_system_prompt = """List the verifiable requirements of completing the user prompt.
The listed requirements will be forwarded to agents those understand them.

Rules:
-Respond with a list of requirements.
-Do not respond with data.
-Extract the requirements only from the user prompt, do not speculate.
-One requirement can contain only one step.
"""


def requirements_text(message: str):
    messages = [
        {"role": "system", "content": requirements_system_prompt},
        {"role": "user", "content": message}
    ]
    requirements = llm.chat(messages)
    return requirements


def _test():
    res = requirements_text("List the 3 most recent projects of the company, briefly describe their goal.")
    print(res.content)


if __name__ == "__main__":
    _test()
