from src.interface2.plan_then_execute_v2.models import llm_deterministic
from src.interface2.plan_then_execute_v2.planner import planner_rules, plan_schema, planner_capabilities, \
    symbolic_reference

llm = llm_deterministic

given_normal = """Given:
- the original goal
- the current plan and the previous outputs
- the progress of the plan"""

task_normal = """Your task:
- Update the missing or inaccurate inputs in the next steps.
- Add or remove steps only if necessary.
- ALWAYS ensure to give the necessary input arguments to the next steps."""

given_error = """Given:
- the original goal
- the current plan and the previous outputs
- the error in the plan
- the progress of the plan"""

task_error = """Your task:
- Observe the error message and fix it.
- Update the missing or inaccurate inputs in the next steps.
- ALWAYS ensure to give the necessary input arguments to the next steps."""

introduction_normal = """You are re-planning.
Output a updated JSON plan by using the PLAN SCHEMA.
Think step by step about the changes those you must implement before the JSON."""

introduction_error = """You are re-planning to FIX AN ERROR.
Output a updated JSON plan by using the PLAN SCHEMA.
Briefly think about the changes those you must implement before building the JSON."""


def get_system_prompt(introduction: str, given: str, task: str):
    return f"""{introduction}


{given}


{task}


{symbolic_reference}


{planner_rules}


{plan_schema}


{planner_capabilities}
"""


def re_plan(goal: str, plan: str, next_steps: list[int], error: str | None = None):
    text = "THE GOAL:\n\n" + goal
    text += "\n\n\nTHE PLAN:\n\n" + plan
    if error:
        text += "\n\n\nERROR MESSAGE:\n" + error
    text += "\n\n\nNEXT STEPS: " + ", ".join(map(str, next_steps))

    system_prompt: str
    if not error:
        system_prompt = get_system_prompt(introduction_normal, given_normal, task_normal)
    else:
        system_prompt = get_system_prompt(introduction_error, given_error, task_error)
    print(text)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    plan = llm.chat(messages)
    return plan


def test1():
    e_goal = "List the 3 most recent projects of the company, briefly describe their goal."
    plan_json = """[
            {
                "id": "1",
                "capability": "DB_SCHEMA",
                "inputs": {
                    "scope": "projects"
                },
                "description": "Get schema for projects table.",
                "depends_on": [].
                "outputs": {
                    "table_schemas": {
                        "projects": [
                            "id": "integer",
                            "title": "string",
                            "description": "string",
                            "created_at": "datetime"
                        ]
                    }
                }
            },
            {
                "id": "2",
                "capability": "DB_QUERY",
                "inputs": {
                    "sql": "SELECT * FROM projects ORDER BY start_date DESC LIMIT 3;"
                },
                "description": "Retrieve the 3 most recent project records from the database.",
                "depends_on": ["1"]
            },
            {
                "id": "3",
                "capability": "SUMMARIZE",
                "inputs": {
                    "text": "2.rows[*].goal",
                    "max_length": 50
                },
                "description": "Summarize the goal of each project.",
                "depends_on": ["2"]
            }
        ]
    }"""
    res = re_plan(e_goal, plan_json, [1])
    print(res.content)


def test2():
    # The step to update has hallucinated symbolic syntax.
    e_goal = "List the 3 most recent projects of the company, briefly describe their goal."
    plan_json = """[
    {
        "id": 1,
        "capability": "DB_SCHEMA",
        "description": "Get the schema of the projects table to understand its structure.",
        "include_in_final_answer": false,
        "output": {
            "table_schemas": {
                "projects": {
                    "id": "INTEGER",
                    "title": "TEXT",
                    "description": "TEXT",
                    "created_at": "TIMESTAMP"
                }
            }
        },
        "inputs": {
            "scope": "projects"
        },
        "completed": true
    },
    {
        "id": 2,
        "capability": "DB_QUERY",
        "description": "Retrieve the titles, descriptions, and creation dates of the three most recent projects.",
        "include_in_final_answer": false,
        "output": {
            "rows": "...",
            "row_count": 3,
            "schema": {
                "title": "str",
                "description": "str",
                "created_at": "int"
            }
        },
        "inputs": {
            "sql": "SELECT title, description, created_at FROM projects ORDER BY created_at DESC LIMIT 3"
        },
        "depends_on": [
            1
        ],
        "completed": true
    },
    {
        "id": 3,
        "capability": "SUMMARIZE",
        "description": "Summarize the descriptions of the three most recent projects.",
        "include_in_final_answer": true,
        "inputs": {
            "texts": "1.description",
            "max_length": 50
        },
        "depends_on": [
            2
        ]
    }
]
    }"""
    res = re_plan(e_goal, plan_json, [2])
    print(res.content)


def test3():
    # The step to update has unknown input
    e_goal = "List the 3 most recent projects of the company, briefly describe their goal."
    plan_json = """[
    {
        "id": 1,
        "capability": "DB_SCHEMA",
        "description": "Get schema for projects table to understand its structure.",
        "include_in_final_answer": false,
        "output": {
            "table_schemas": {
                "projects": {
                    "id": "INTEGER",
                    "title": "TEXT",
                    "description": "TEXT",
                    "created_at": "TIMESTAMP"
                }
            }
        },
        "inputs": {
            "scope": "projects"
        },
        "completed": true
    },
    {
        "id": 2,
        "capability": "DB_QUERY",
        "description": "Retrieve the 3 most recent project records from the database.",
        "include_in_final_answer": false,
        "output": {
            "rows": "@2",
            "row_count": 3,
            "schema": {
                "id": "int",
                "title": "str",
                "description": "str"
            }
        },
        "inputs": {
            "sql": "SELECT id, title, description FROM projects ORDER BY created_at DESC LIMIT 3"
        },
        "depends_on": [
            1
        ],
        "completed": true
    },
    {
        "id": 3,
        "capability": "SUMMARIZE",
        "description": "Summarize the goals of the selected projects.",
        "include_in_final_answer": true,
        "depends_on": [
            2
        ],
        "inputs": {}
    }
]"""
    res = re_plan(e_goal, plan_json, [2])
    print(res.content)


if __name__ == "__main__":
    test3()
