import pandas as pd
from sqlalchemy import text
from agentforge.database.connection import engine


def execute_query(query: str):
    with engine.connect() as connection:
        result = connection.execute(text(query))
        columns = result.keys()
        rows = result.fetchall()
        df = pd.DataFrame(rows, columns=columns)
        return df