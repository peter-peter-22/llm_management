from src.interface2.plan_then_execute_v2.models import llm_deterministic

llm = llm_deterministic

planner_capabilities = """AVAILABLE CAPABILITIES

[DB_SCHEMA]
Inputs:
- scope: (projects | employees) REQUIRED.
Outputs:
- entity_fields
Description:
- Returns the schema of the tables in a scope.

[DB_QUERY]
Inputs:
- sql
Outputs:
- rows
Description:
- Text fields are raw.

[SUMMARIZE]
Inputs:
- text, max_length
Outputs:
- summary
Description:
- Use symbolic reference for bulk summary: 2.rows[*].title"""

plan_schema = """PLAN SCHEMA
"steps": {
    "items": {
        "id": {"type":"string"},
        "capability": {"type":"string"},
        "inputs": {
            "type": "object"
            "description": "Use '__UNKNOWN__' for still unknown data. Use symbolic references for step outputs." 
        },
        "description": {"type":"string"},
        "depends_on": {
            "type": "array",
            "items": "int"
        }
    },
    "type": "array"
}"""

planner_rules = """Rules of step creation:
- Use only known capabilities.
- Do not guess schema or SQL.
- If an input is unknown, use "__UNKNOWN__".
- Reference step outputs symbolically: 1.table_schemas.projects."""

planner_system_prompt = f"""
You are a planner.
Output a JSON plan by using the PLAN SCHEMA.


{planner_rules}


{plan_schema}


{planner_capabilities}
"""


def create_plan(message: str):
    messages = [
        {"role": "system", "content": planner_system_prompt},
        {"role": "user", "content": message}
    ]
    plan = llm.chat(messages)
    return plan


def _test():
    res = create_plan("List the 3 most recent projects of the company, briefly describe their goal.")
    print(res.content)
    """```json
{
    "steps": [
        {
            "id": "1",
            "capability": "DB_SCHEMA",
            "inputs": {
                "scope": "projects"
            },
            "description": "Get schema for projects table.",
            "depends_on": []
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
}
```"""


if __name__ == "__main__":
    _test()
