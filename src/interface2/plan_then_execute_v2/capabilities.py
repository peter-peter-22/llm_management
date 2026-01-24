from typing import Optional

from pydantic import validate_call, ConfigDict, SkipValidation

from src.interface2.plan_then_execute_v2.database.get_schema import get_and_describe_tables
from src.interface2.plan_then_execute_v2.database.query import query_with_schema
from src.interface2.plan_then_execute_v2.entites import StepOutput, StepOutputField, Capability, ExecutionContext
from src.interface2.plan_then_execute_v2.symbolic_reference import resolve_symbolic_reference


# The planner cannot use the parameters yet
class DbQuery(Capability):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def execute(self, ctx: SkipValidation[ExecutionContext], sql: str, parameters: Optional[tuple] = None):
        rows, schema = query_with_schema(sql, parameters)
        return StepOutput(values={
            "rows": StepOutputField(value=rows, display=False),
            "row_count": StepOutputField(value=len(rows), display=True),
            "schema": StepOutputField(value=(schema if schema else "unknown"), display=True)
        })


table_scopes = {
    "projects": ["projects"],
    "employees": ["users"]
}


class DbSchema(Capability):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def execute(self, ctx: SkipValidation[ExecutionContext], scope: str):
        try:
            table_names = table_scopes[scope]
        except KeyError:
            raise ValueError(f"Scope {scope} is not valid")
        tables = get_and_describe_tables(table_names)
        res = StepOutput.model_construct(values={
            "table_schemas": StepOutputField.model_construct(value=tables, display=True)
        })
        return res


# Placeholder, returns the original texts.
class Summarize(Capability):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def execute(self, ctx: SkipValidation[ExecutionContext], texts: str, max_length: int):
        real_texts = resolve_symbolic_reference(ctx.plan, texts)
        return StepOutput.model_construct(values={
            "summaries": StepOutputField.model_construct(value=real_texts, display=False)
        })
