from src.interface2.plan_then_execute_v2.models import llm_deterministic
from src.interface2.plan_then_execute_v2.planner import planner_rules, plan_schema, planner_capabilities

llm = llm_deterministic

planner_system_prompt = f"""
You are re-planning.
Given:
- the original goal
- the current plan and the previous outputs
- the ids of the completed steps since the last re-planning


Your task:
- Observe the outputs of the last completed step and update the missing or inaccurate information in the next steps.
- Add or remove steps ONLY if necessary.
- __UNKNOWN__ is not a valid input, replace it when possible.


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
        "inputs": [],
        "description": "Get schema for 'projects'",
        "depends_on": [],
        "outputs": {
            "table_schemas": {
                "projects": [
                    "id": "integer",
                    "title": "string",
                    "description": "string",
                    "created_at": "datetime"
                ]
            }
        },
        "status": "completed"
    },
    {
        "id": "2",
        "capability": "DB_QUERY",
        "inputs": [
            {
                "sql": "SELECT * FROM projects ORDER BY start_date DESC LIMIT 3"
            }
        ],
        "description": "Fetch the 3 most recent project records from the database.",
        "depends_on": ["1"],
        "status": "next"
    },
    {
        "id": "3",
        "capability": "SUMMARIZE",
        "inputs": [
            {
                "text": "__UNKNOWN__",
                "max_length": 50
            }
        ],
        "description": "Summarize the goal of each project.",
        "depends_on": ["2"]
    }
]"""
    res = re_plan(e_goal, plan_json, [1])
    print(res.content)
    """The plan needs to be updated because the SQL query in step 2 is incorrect. It should order by `created_at` instead of `start_date`. Additionally, we need to ensure that the description from step 2 is correctly passed to step 3 for summarization.

Here's the revised plan:

```json
[
    {
        "id": "1",
        "capability": "DB_SCHEMA",
        "inputs": [],
        "description": "Get schema for 'projects'",
        "depends_on": [],
        "outputs": {
            "table_schemas": {
                "projects": [
                    {"id": "integer"},
                    {"title": "string"},
                    {"description": "string"},
                    {"created_at": "datetime"}
                ]
            }
        },
        "status": "completed"
    },
    {
        "id": "2",
        "capability": "DB_QUERY",
        "inputs": [
            {
                "sql": "SELECT * FROM projects ORDER BY created_at DESC LIMIT 3"
            }
        ],
        "description": "Fetch the 3 most recent project records from the database.",
        "depends_on": ["1"],
        "status": "completed"
    },
    {
        "id": "3",
        "capability": "SUMMARIZE",
        "inputs": [
            {
                "text": "__UNKNOWN__",
                "max_length": 50
            }
        ],
        "description": "Summarize the goal of each project.",
        "depends_on": ["2"]
    }
]
```

In this revised plan:
- Step 1 remains unchanged.
- Step 2 is updated to use `created_at` instead of `start_date`.
- Step 3 uses symbolic reference `2.rows[*].description` for summarizing the goal of each project."""


def test2():
    e_goal = "List the 3 most recent projects of the company, briefly describe their goal."
    plan_json = """[
    {
        "id": "1",
        "capability": "DB_SCHEMA",
        "inputs": [],
        "description": "Get schema for 'projects'",
        "depends_on": [],
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
        "inputs": [
            {
                "sql": "SELECT * FROM projects ORDER BY created_at DESC LIMIT 3"
            }
        ],
        "description": "Fetch the 3 most recent project records from the database.",
        "depends_on": ["1"],
        "outputs": {
         "rows": {
            count: "3",
            schema: "1.table_schemas.projects"
         }
        }
    },
    {
        "id": "3",
        "capability": "SUMMARIZE",
        "inputs": [
            {
                "text": "__UNKNOWN__",
                "max_length": 50
            }
        ],
        "description": "Summarize the goal of each project.",
        "depends_on": ["2"]
    }
]"""
    res = re_plan(e_goal, plan_json, [2])
    print(res.content)
    # Errors:
    # the llm modifies the status even when told to not
    # works better without the status field
    """Given that step 2 has completed and we have fetched the 3 most recent projects, let's update step 3 to use the actual data from step 2.

Here is the updated plan:

```json
[
    {
        "id": "1",
        "capability": "DB_SCHEMA",
        "inputs": [],
        "description": "Get schema for 'projects'",
        "depends_on": [],
        "outputs": {
            "table_schemas": {
                "projects": [
                    {"id": "integer"},
                    {"title": "string"},
                    {"description": "string"},
                    {"created_at": "datetime"}
                ]
            }
        }
    },
    {
        "id": "2",
        "capability": "DB_QUERY",
        "inputs": [
            {
                "sql": "SELECT * FROM projects ORDER BY created_at DESC LIMIT 3"
            }
        ],
        "description": "Fetch the 3 most recent project records from the database.",
        "depends_on": ["1"],
        "outputs": {
            "rows": {
                "count": "3",
                "schema": "1.table_schemas.projects"
            }
        }
    },
    {
        "id": "3",
        "capability": "SUMMARIZE",
        "inputs": [
            {
                "text": "2.rows[*].description",
                "max_length": 50
            }
        ],
        "description": "Summarize the goal of each project.",
        "depends_on": ["2"]
    }
]
```

In this updated plan:
- Step 3 now uses `2.rows[*].description` to get the description of each project, which will be used for summarization."""


if __name__ == "__main__":
    test2()
