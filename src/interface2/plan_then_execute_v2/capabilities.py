from typing import Optional

from pydantic import validate_call

from src.interface2.plan_then_execute_v2.database.get_schema import describe_all_tables
from src.interface2.plan_then_execute_v2.database.query import query_to_dicts
from src.interface2.plan_then_execute_v2.entites import StepOutput, StepOutputField, Capability


class DbQuery(Capability):
    @validate_call
    def execute(self, query: str, parameters: Optional[tuple] = None):
        rows = query_to_dicts(query, parameters)
        return StepOutput.model_construct(output={
            "rows": StepOutputField.model_construct(value=rows, display=False)
        })


table_scopes = {
    "projects": ["projects"],
    "employees": ["users"]
}


class DbSchema(Capability):
    def execute(self, scope: str):
        rows = describe_all_tables()
        res = StepOutput.model_construct(values={
            "rows": StepOutputField.model_construct(value=rows, display=False)
        })
        return res


class Summarize(Capability):
    def execute(self, query: str, parameters: Optional[tuple] = None):
        rows = query_to_dicts(query, parameters)
        return StepOutput.model_construct(output={
            "rows": StepOutputField.model_construct(value=rows, display=False)
        })
