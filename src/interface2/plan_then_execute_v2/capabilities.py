from typing import Optional

from src.interface2.plan_then_execute_v2.database.query import query_to_dicts
from src.interface2.plan_then_execute_v2.types import StepOutput, StepOutputField, Capability


class DbQuery(Capability):
    def execute(self, query: str, parameters: Optional[tuple] = None):
        rows = query_to_dicts(query, parameters)
        return StepOutput.model_construct(output={
            "rows": StepOutputField.model_construct(value=rows, display=False)
        })


class DbSchema(Capability):
    def execute(self, query: str, parameters: Optional[tuple] = None):
        rows = query_to_dicts(query, parameters)
        return StepOutput.model_construct(output={
            "rows": StepOutputField.model_construct(value=rows, display=False)
        })


class Summarize(Capability):
    def execute(self, query: str, parameters: Optional[tuple] = None):
        rows = query_to_dicts(query, parameters)
        return StepOutput.model_construct(output={
            "rows": StepOutputField.model_construct(value=rows, display=False)
        })
