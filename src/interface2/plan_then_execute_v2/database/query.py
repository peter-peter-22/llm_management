import sqlite3
from contextlib import closing
from typing import List, Dict, Any, Optional

from src.interface2.plan_then_execute_v2.database.initialize import conn


def query_to_dicts(
        query: str,
        parameters: Optional[tuple] = None
) -> List[Dict[str, Any]]:
    """
    Execute a SQL query and return results as a list of dictionaries.

    Args:
        query: SQL query string
        parameters: Optional tuple of query parameters for parameterized queries

    Returns:
        List of dictionaries where keys are column names and values are row data

    Raises:
        sqlite3.Error: If there's an error executing the query
    """
    try:
        # Use row_factory to access columns by name
        conn.row_factory = sqlite3.Row

        with closing(conn.cursor()) as cursor:
            # Execute the query with optional parameters
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            # Fetch all rows and convert to dictionaries
            rows = cursor.fetchall()

            # Convert each sqlite3.Row to a dictionary
            result = [dict(row) for row in rows]

            return result

    except sqlite3.Error as e:
        # Re-raise the exception with additional context
        raise sqlite3.Error(f"Database error: {e}") from e


def _test():
    res = query_to_dicts("select * from projects")
    print(res)


if "__main__" == __name__:
    _test()
