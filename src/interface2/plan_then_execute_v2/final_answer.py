import json

from src.interface2.plan_then_execute_v2.entites import StepOutput, ProcessedPlan, ProcessedStep, StepOutputField
from src.interface2.plan_then_execute_v2.models import llm_deterministic

llm = llm_deterministic

system_prompt = """You are formatting an answer for the user.

Rules:
- Base your answer ONLY on the provided data.
- You are provided with all data that is needed for your answer, do not add new information.
- Use the data exactly as provided, unless transformation is explicitly required.
- The 'source_operation' field of the provided data tells what request this data answered."""


def final_answer(user_prompt: str, plan: ProcessedPlan):
    included_facts = []
    for step in plan.steps.values():
        if step.include_in_final_answer:
            included_facts.append({
                "data": step.outputs.to_dict(),
                "source_operation": step.description
            })

    text = f"[USER PROMPT]\n\n{user_prompt}\n\n\n[DATA]\n\n{json.dumps(included_facts, indent=4)}"
    print(text)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    return llm.chat(messages)


def _test():
    plan = ProcessedPlan(steps={
        3: ProcessedStep(
            id=3,
            capability="SUMMARIZE",
            description="Summarize the descriptions of the selected projects.",
            outputs=StepOutput(
                values={
                    "summaries": StepOutputField(
                        value=[
                            "The second episode of the ball game series. Same ball, different levels.",
                            "An AI powered OCR and translator for images.",
                            "A website for internal discussions of the a company."
                        ],
                        display=False
                    )
                }
            ),
            inputs={},
            include_in_final_answer=True
        )
    })
    user_prompt = "List the 3 most recent projects of the company, briefly describe their goal."
    res = final_answer(user_prompt, plan)
    print(res.content)
    """The three most recent projects of the company, along with their brief goals, are as follows:

1. An AI powered OCR and translator for images.
2. A website for internal discussions of the company.
3. The second episode of the ball game series. Same ball, different levels."""


if __name__ == '__main__':
    _test()
