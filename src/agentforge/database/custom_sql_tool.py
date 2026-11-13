
import sqlglot
from sqlglot import exp
from langchain.tools import tool

from agentforge.database.query_executor import execute_query


def validate_sql(query: str):
    statements = sqlglot.parse(query, read="mysql")

    if len(statements) != 1:
        raise ValueError("Only one SQL statement is allowed.")

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        raise ValueError("Only SELECT queries are allowed.")

    return True


@tool
def execute_sql(query: str):
    """Execute a read-only SELECT query against the Agent Forge database."""

    validate_sql(query)

    result = execute_query(query)

    return result.to_json(orient="records")
