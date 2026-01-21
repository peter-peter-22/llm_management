from typing import NamedTuple

from src.interface2.plan_then_execute_v2.database.initialize import conn, initialize


class Column(NamedTuple):
    name: str
    type: str
    nullable: int
    default: str | None
    primary_key: int


class Table(NamedTuple):
    name: str
    columns: list[Column]


def get_schema(table_name: str):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_raw = cursor.fetchall()
    cursor.close()
    # for column in schema:
    #     print(
    #         f"Column: {column[1]}, Type: {column[2]}, Nullable: {column[3]}, Default: {column[4]}, Primary Key: {column[5]}")
    columns_formatted: list[Column] = [Column(column[1], column[2], column[3], column[4], column[5]) for column in
                                       columns_raw]
    schema = Table(table_name, columns_formatted)
    return schema


def list_tables():
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT name
                   FROM sqlite_master
                   WHERE type = 'table';
                   """)
    tables = cursor.fetchall()
    names = list(filter(lambda t: t != 'sqlite_sequence', [table[0] for table in tables]))
    cursor.close()
    return names


def describe_table(table: Table):
    table_text = "entity: " + table.name + "\nfields:\n"
    table_text += "\n".join([
        f"-{column.name}: {column.type}"
        for column in table.columns
    ])
    return table_text


def describe_schema(tables: list[Table]):
    return "\n\n".join([
        describe_table(table)
        for table in tables
    ])


def get_and_describe_schema():
    table_names = list_tables()
    tables = [get_schema(table_name) for table_name in table_names]
    return describe_schema(tables)


if __name__ == '__main__':
    initialize()
    text = get_and_describe_schema()
    print(text)
    conn.close()
