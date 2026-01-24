import json
import re
from typing import NamedTuple, Literal, Optional, Any

from src.interface2.plan_then_execute_v2.entites import ProcessedPlan, ProcessedStep, StepOutput, StepOutputField


class Directory(NamedTuple):
    name: str
    index: Optional[int | Literal["*"]]


class SymbolicReference(NamedTuple):
    step_id: int
    path: list[Directory]

    def dump_path(self, depth: int | None = None) -> str:
        """Form a string from the path."""
        if depth is None:
            return ".".join([str(self.step_id), [p.name for p in self.path[:depth]]])
        text = str(self.step_id)
        if depth == 0:
            return text
        text += "." + ".".join([p.name for p in self.path[:depth]])
        return text


def parse_symbolic_reference(text: str):
    words = text.split(".")
    step_id = int(words[0])
    fields: list[Directory] = []
    for word in words[1:]:
        s = re.split("[\\[,\\]]", word)
        name = s[0]
        if name == "output":  # Skip this directory
            continue
        if len(s) == 1:
            fields.append(Directory(name, None))
            continue
        index = s[1]
        if index == "*":
            fields.append(Directory(name, index))
            continue
        try:
            fields.append(Directory(name, int(index)))
        except ValueError:
            raise ValueError("Invalid index. The index must be an integer or '*'")
    return SymbolicReference(step_id, fields)


def _select_dir(data: Any, ref: SymbolicReference, dir_name: str, i: int, is_array: bool):
    if not data:
        if is_array:
            raise ValueError(
                f"At least 1 element of the list '{ref.dump_path(i)}' is None, failed to read field '{dir_name}'")
        else:
            raise ValueError(f"'{ref.dump_path(i)}' is None, failed to read field '{dir_name}'")
    if not isinstance(data, dict):
        raise ValueError(f"'{ref.dump_path(i)}' is not a dictionary.")
    try:
        return data[dir_name]
    except KeyError:
        raise ValueError(
            f"Step '{ref.step_id}' does not have an output named '{ref.dump_path(i + 1)}'.")


def _travel_path(data: Any, ref: SymbolicReference):
    # Travel on the path
    for i, directory in enumerate(ref.path):
        # Select the searched field
        if isinstance(data, list):
            data = [
                _select_dir(d, ref, directory.name, i, True)
                for d in data
            ]
        else:
            data = _select_dir(data, ref, directory.name, i, False)

        # Process array operations
        if directory.index is not None:
            if not isinstance(data, list):
                raise ValueError(f"'{ref.dump_path(i + 1)}' is not a list.")
            if isinstance(directory.index, int):
                try:
                    data = data[directory.index]
                except IndexError:
                    raise ValueError(f"'{directory.index}' is out of index range. List length: {len(data)}")
    return data


def resolve_symbolic_reference(plan: ProcessedPlan, ref: str):
    try:
        # Parse and validate the reference
        parsed = parse_symbolic_reference(ref)
    except ValueError as e:
        raise ValueError(f"Failed to parse symbolic reference: '{ref}'\n" + e.__str__())
    try:
        try:
            step = plan.steps[parsed.step_id]
        except KeyError:
            raise ValueError(f"Step '{parsed.step_id}' does not exists.")
        if len(parsed.path) == 0:
            raise ValueError("The reference must refer to a field of the output.")
        data = step.outputs
        if not data:
            raise ValueError(f"Step '{parsed.step_id}' has no outputs.")

        # Travel the path
        return _travel_path(data.to_dict(), parsed)
    except ValueError as e:
        raise ValueError(f"Invalid symbolic reference in step '{parsed.step_id}': '{ref}'\n" + e.__str__())


def _test():
    print("Parsing", json.dumps(parse_symbolic_reference("2.rows[*].description"), indent=2))

    p_plan = ProcessedPlan(steps={
        1: ProcessedStep(
            id=1,
            capability="",
            inputs={},
            outputs=StepOutput(values={
                "text": StepOutputField(value="direct text", display=False),
                "texts": StepOutputField(value=["element", "element"], display=False),
                "rows": StepOutputField(
                    value=[
                        {"id": 1, "text": "row"},
                        {"id": 2, "text": "row"},
                    ],
                    display=False
                ),
                "nested": StepOutputField(
                    value={
                        "text": "nested text",
                        "texts": StepOutputField(value=["element", "element"], display=False),
                        "rows": [
                            {"id": 1, "text": "nested row"},
                            {"id": 2, "text": "nested row"},
                        ]
                    },
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
    _print_ref("1.text")
    _print_ref("1.nested.text")
    _print_ref("1.texts")
    _print_ref("1.texts[*]")
    _print_ref("1.rows[*].text")
    _print_ref("1.rows.text")
    _print_ref("1.rows[0].text")

    # Error
    _print_ref("0.text")
    _print_ref("1.nothing")
    _print_ref("1.rows[2].text")
    _print_ref("1.rows.rows")
    _print_ref("invalid...df.fsd.ds.fd.fs")


if __name__ == "__main__":
    _test()
