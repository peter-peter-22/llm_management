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
                "depends_on": ["1"],
                "outputs": {
                    "row_count": 3,
                    "rows": "..."
                    "schema": "1.table_schemas.projects"
                }
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
    res = re_plan(e_goal, plan_json, [2])
    print(res.content)
    """Given that step 2 has completed, we have the rows from the most recent projects. We need to update step 3 to correctly reference these outputs and ensure it provides a summary of the project goals.

Here is the updated plan:

```json
[
    {
        "id": "1",
        "capability": "DB_SCHEMA",
        "inputs": {
            "scope": "projects"
        },
        "description": "Get schema for projects table.",
        "depends_on": [],
        "outputs": {
            "table_schemas": {
                "projects": [
                    {"id": "integer", "title": "string", "description": "string", "created_at": "datetime"}
                ]
            }
        }
    },
    {
        "id": "2",
        "capability": "DB_QUERY",
        "inputs": {
            "sql": "SELECT * FROM projects ORDER BY created_at DESC LIMIT 3;"
        },
        "description": "Retrieve the 3 most recent project records from the database.",
        "depends_on": ["1"],
        "outputs": {
            "row_count": 3,
            "rows": "__UNKNOWN__",
            "schema": "1.table_schemas.projects"
        }
    },
    {
        "id": "3",
        "capability": "SUMMARIZE",
        "inputs": {
            "text": "2.rows[*].description",  // Corrected to 'description' from 'goal'
            "max_length": 50
        },
        "description": "Summarize the goal of each project.",
        "depends_on": ["2"]
    }
]
```

### Explanation:
- **Step 1**: No change, as it correctly retrieves the schema for the projects table.
- **Step 2**: No change, as it correctly queries the database to get the most recent three projects.
- **Step 3**: Updated to reference `description` instead of `goal`, which is more likely the field containing the project goals.

Since step 2 has already completed and provided the rows, we can proceed with step 3 using the correct field name."""


if __name__ == "__main__":
    test2()
