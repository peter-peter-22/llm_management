import json
from typing import Callable

from src.interface2.plan_then_execute_v2.entites import Plan

type TextExtractor = Callable[[str], str | None]


def try_triple_quotation_mark(text: str):
    # Find the last '```json' and last '```'
    start = text.rfind('```json')
    end = text.rfind('```')

    if start == -1 or end == -1 or start > end:
        return None

    # Extract the substring
    json_str = text[start + 7:end].strip()

    # Parse and return
    return json_str


def try_square_bracket(text: str):
    # Find the first '[' and last ']'
    start = text.find('[')
    end = text.rfind(']')

    if start == -1 or end == -1 or start > end:
        return None

    # Extract the substring
    json_str = text[start:end + 1]

    # Parse and return
    return json_str


extractors: list[TextExtractor] = [
    try_triple_quotation_mark,
    try_square_bracket
]  # Add a LLM based extractor as last fallback


def extract_json(text: str):
    for extractor in extractors:
        result = extractor(text)
        if result is not None:
            try:
                return json.loads(result)
            except json.decoder.JSONDecodeError as e:
                print("Failed to decode the found json", e)
                continue
    raise ValueError("Could not extract json from text:\n", text)


def extract_plan(text: str):
    # Get JSON
    j = extract_json(text)

    # Ensure consistent format
    # The format randomly changes between "[...]" and "{'steps':[...]}"
    if isinstance(j, dict) and "steps" in j:
        j = j["steps"]

    # Validate
    p = Plan(steps=j)
    return p


def _test():
    example = """Given that step 2 has completed and we have fetched the 3 most recent projects, let's update step 3 to use the actual data from step 2.

Here is the updated plan:

```json
{
    "steps": [
        {
            "id": "1",
            "capability": "DB_SCHEMA",
            "inputs": {
                "scope": "projects"
            },
            "description": "Get schema for projects table.",
            "depends_on": [],
            "remove_this_field": "remove_this_field"
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
```

In this updated plan:
- Step 3 now uses `2.rows[*].description` to get the description of each project, which will be used for summarization."""
    res = extract_plan(example)
    print(res.model_dump_json(indent=2))

    try:
        bad_example = """{
    "steps": [
    {
        "id": 1,
        "capability": "DB_SCHEMA",
        "description": "Get the schema for the projects table to understand its structure.",
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
        }
    },
    {
        "id": 2,
        "capability": "DB_QUERY",
        "description": "Retrieve the details of the three most recent projects.",
        "include_in_final_answer": false,
        "inputs": {
            "sql": "SELECT * FROM projects ORDER BY start_date DESC LIMIT 3"
        },
        "depends_on": [
            1
        ]
    },
    {
        "id": 3,
        "capability": "SUMMARIZE",
        "description": "Summarize the goals of the three most recent projects.",
        "include_in_final_answer": true,
        "inputs": {
            "texts": "2.rows[*].goal",
            "max_length": 50
        },
        "depends_on": [
            2
        ]
    }
]"""
        res = extract_plan(bad_example)
        print(res.model_dump_json(indent=2))
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    _test()
