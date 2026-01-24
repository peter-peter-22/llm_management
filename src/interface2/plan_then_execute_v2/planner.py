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
- texts: symbolic reference 
- max_length: int
Outputs:
- summary
Description:
- Summarize an array of texts."""

plan_schema = """PLAN SCHEMA
"steps": {
    "items": {
        "id": {
            "type": "int"
        },
        "capability": {
            "type": "string"
        },
        "inputs": {
            "type": "object" 
        },
        "description": {
            "type": "string"
        },
        "depends_on": {
            "type": "array",
            "items": "int"
        },
        "include_in_final_answer": {
            "type": "bool"
        }
    },
    "type": "array"
}"""

planner_rules = """Rules of step creation:
- Use only known capabilities.
- Do not guess tables, SQL and outputs."""

symbolic_reference = """SYMBOLIC REFERENCE usage: 
- Use rows returned by the DB_QUERY as input by referring to the step id and the selected column: '@1.column_name'"""

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
