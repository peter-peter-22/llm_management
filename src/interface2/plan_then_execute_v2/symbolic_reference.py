import json
import re
from typing import NamedTuple, Literal, Optional, Any


class Field(NamedTuple):
    name: str
    index: Optional[int | Literal["*"]]


class SymbolicReference(NamedTuple):
    step_id: int
    path: list[Field]


def parse_symbolic_reference(text: str):
    words = text.split(".")
    step_id = int(words[0])
    fields: list[Field] = []
    for word in words[1:]:
        s = re.split("[\\[,\\]]", word)
        name = s[0]
        if len(s) == 1:
            fields.append(Field(name, None))
            continue
        index = s[1]
        if index == "*":
            fields.append(Field(name, index))
            continue
        try:
            fields.append(Field(name, int(index)))
        except ValueError:
            raise ValueError("Invalid index. The index must be an integer or '*'")
    return SymbolicReference(step_id, fields)


def open_symbolic_reference(ref: SymbolicReference, outputs: dict[str, Any]):
    pass


def _test():
    e = "2.rows[*].description"
    ref = parse_symbolic_reference(e)
    print(json.dumps(ref, indent=2))


if __name__ == "__main__":
    _test()
