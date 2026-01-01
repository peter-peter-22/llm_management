from typing import Literal

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.langchain.system_level_scaffolding.database.initialize import *

initialize()

type SortBy = Literal["created_at", "title"]
type SortDirection = Literal["ascending", "descending"]


class GetProjectsInput(BaseModel):
    count: int = Field(description="Number of projects to return.", default=5)
    sort: SortBy = Field(description="Ordering method.", default="created_at")
    sort_direction: SortDirection = Field(description="Ordering direction.", default="descending")


@tool(args_schema=GetProjectsInput, response_format="content_and_artifact")
def get_projects(count: int, sort: SortBy, sort_direction: SortDirection):
    """Retrieve the projects from the database with adjustable sorting."""
    cursor = conn.cursor()
    cursor.execute("""SELECT *
                      FROM projects
                      LIMIT {count}
                      ORDER BY {sort} {sort_direction}
                   """.format(
        count=count,
        sort=sort,
        sort_direction="ASC" if sort_direction == "ascending" else "DESC"
    ))
    projects = cursor.fetchall()

    serialized = "\n\n".join(
        (
            f"Id: {project.id}\nTitle: {project.title}\nDescription: {project.description}\nCreatedAt: {project.created_at}\n")
        for project in projects
    )
    print("Retrieved:\n", serialized)
    return serialized, projects


class GetProjectsInputFiltered(BaseModel):
    query: str = Field(description="Search text.")
    count: int = Field(description="Number of projects to return.", default=5)
    sort: SortBy = Field(description="Ordering method.", default="created_at")
    sort_direction: SortDirection = Field(description="Ordering direction.", default="descending")


@tool(args_schema=GetProjectsInputFiltered)
def filter_projects(query: str, count: int, sort: SortBy, sort_direction: SortDirection):
    """Get the projects where the title or description contains the searched keyword from the database with adjustable sorting."""
    cursor = conn.cursor()
    cursor.execute("""SELECT *
                      FROM projects
                      WHERE title LIKE '%{query}%' OR description LIKE '%{query}%'
                      LIMIT {count}
                      ORDER BY {sort} {sort_direction}
                   """.format(
        query=query,
        count=count,
        sort=sort,
        sort_direction="ASC" if sort_direction == "ascending" else "DESC"
    ))
    projects = cursor.fetchall()
    return projects


tools = [get_projects]
