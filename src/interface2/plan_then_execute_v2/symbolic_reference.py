import json
from typing import NamedTuple

from src.interface2.plan_then_execute_v2.entites import ProcessedPlan, ProcessedStep, StepOutput, StepOutputField


class SymbolicReference(NamedTuple):
    step_id: int
    column: str | None = None


def parse_symbolic_reference(text: str):
    try:
        words = text.split(".")
        step_id = int(words[0][1:])
        if len(words) == 2:
            column = words[1]
            return SymbolicReference(step_id, column)
        if len(words) == 1:
            return SymbolicReference(step_id)
        else:
            raise ValueError("More than 1 '.' found but max 1 can be present.")
    except Exception:
        raise ValueError("Failed to parse symbolic reference.")


def resolve_symbolic_reference(plan: ProcessedPlan, ref: str):
    # Parse and validate the reference
    parsed = parse_symbolic_reference(ref)
    try:
        # Validate the selected step
        try:
            step = plan.steps[parsed.step_id]
        except KeyError:
            raise ValueError(f"Step '{parsed.step_id}' does not exists.")
        if not step.outputs:
            raise ValueError(f"Step '{parsed.step_id}' has no outputs.")
        rows = step.outputs.values.get("rows")
        if not rows:
            raise ValueError(f"Step '{parsed.step_id}' has no rows.")
        # Return data
        if not parsed.column:
            return rows.value
        else:
            try:
                return [row[parsed.column] for row in rows.value]
            except KeyError:
                raise ValueError(
                    f"The selected column '{parsed.column}' is not found at the rows of step '{parsed.step_id}'.")

    except ValueError as e:
        raise ValueError(f"Invalid symbolic reference': '{ref}'\n" + e.__str__())


def _test():
    print("Parsing", json.dumps(parse_symbolic_reference("$2.description"), indent=2))

    p_plan = ProcessedPlan(steps={
        1: ProcessedStep(
            id=1,
            capability="",
            inputs={},
            outputs=StepOutput(values={
                "rows": StepOutputField(
                    value=[
                        {"id": 1, "text": "row"},
                        {"id": 2, "text": "row"},
                    ],
                    display=False
                ),
            })
        ),
    })

    def _print_ref(ref: str):
        try:
            print(ref, "\n    ", resolve_symbolic_reference(p_plan, ref))
        except ValueError as e:
            print(ref, "\n    ", e.__str__())

    # Valid
    _print_ref("@1.text")
    _print_ref("@1")

    # Error
    _print_ref("@0")
    _print_ref("@1.nothing")
    _print_ref("invalid...df.fsd.ds.fd.fs")


if __name__ == "__main__":
    _test()
