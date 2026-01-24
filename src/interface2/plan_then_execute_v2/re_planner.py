from src.interface2.plan_then_execute_v2.models import llm_deterministic
from src.interface2.plan_then_execute_v2.planner import planner_rules, plan_schema, planner_capabilities, \
    symbolic_reference

llm = llm_deterministic

planner_system_prompt = f"""
You are re-planning.
Output an updated JSON plan by using the PLAN SCHEMA.

Given:
- the original goal
- the current plan and the previous outputs
- the ids of the completed steps since the last re-planning


Your task:
- Observe the outputs of the last completed step and update the missing or inaccurate information in the next steps.
- Add or remove steps ONLY if necessary.


{symbolic_reference}


{planner_rules}


{plan_schema}


{planner_capabilities}
"""


def re_plan(goal: str, plan: str, last_completed: list[int]):
    text = "THE GOAL:\n\n" + goal
    text += "\n\n\nTHE PLAN:\n\n" + plan
    text += "\n\n\nLAST COMPLETED:\n" + ", ".join(map(str, last_completed))
    print(text)
    messages = [
        {"role": "system", "content": planner_system_prompt},
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
                "texts": "__UNKNOWN__",
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


if __name__ == "__main__":
    test3()
