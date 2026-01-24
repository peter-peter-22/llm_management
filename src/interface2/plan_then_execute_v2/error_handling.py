from typing import Any

from pydantic import ValidationError


def pretty_pydantic_error(e: ValidationError) -> str:
    fields: list[Any] = e.errors()
    pretty_fields = []
    for field in fields:
        field_name: str
        f: tuple = field["loc"]
        if len(f) == 1:
            field_name = f"'{f[0]}'"
        else:
            field_name = str(f)
        m = f"- input: {field_name}, message: {field["msg"]}"
        pretty_fields.append(m)

    msg = "Invalid argument(s):\n" + "\n".join(pretty_fields)
    return msg
