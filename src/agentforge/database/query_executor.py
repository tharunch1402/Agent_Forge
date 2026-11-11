import pandas as pd
from sqlalchemy import text
from agentforge.database.connection import engine
from sqlalchemy.exc import SQLAlchemyError


def execute_query(query: str):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=columns)
            return df

    except SQLAlchemyError as e:
        raise RuntimeError(f"Database execution failed: {e}") from e