import json
from contextlib import closing
from typing import NamedTuple

from src.interface2.plan_then_execute_v2.database.initialize import conn


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
    with closing(conn.cursor()) as cursor:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_raw = cursor.fetchall()
        cursor.close()
        # for column in schema:
        #     print(
        #         f"Column: {column[1]}, Type: {column[2]}, Nullable: {column[3]}, Default: {column[4]}, Primary Key: {column[5]}")
        columns_formatted: list[Column] = [Column(column[1], column[2], column[3], column[4], column[5]) for column
                                           in
                                           columns_raw]
        schema = Table(table_name, columns_formatted)
        return schema


def list_tables():
    with closing(conn.cursor()) as cursor:
        cursor.execute("""
                       SELECT name
                       FROM sqlite_master
                       WHERE type = 'table';
                       """)
        tables = cursor.fetchall()
        names = list(filter(lambda t: t != 'sqlite_sequence', [table[0] for table in tables]))
        return names


def describe_table(table: Table):
    return {
        column.name: column.type
        for column in table.columns
    }


def get_and_describe_table(table_name: str):
    table = get_schema(table_name)
    return describe_table(table)


def get_and_describe_tables(table_names: list[str]):
    return {
        table_name: get_and_describe_table(table_name)
        for table_name in table_names
    }


def describe_all_tables():
    table_names = list_tables()
    return get_and_describe_tables(table_names)


if __name__ == '__main__':
    j = describe_all_tables()
    print(json.dumps(j, indent=2))
    """{
  "projects": {
    "id": "INTEGER",
    "title": "TEXT",
    "description": "TEXT",
    "created_at": "TIMESTAMP"
  },
  "users": {
    "id": "INTEGER",
    "username": "TEXT",
    "full_name": "TEXT",
    "created_at": "TIMESTAMP"
  }
}"""
