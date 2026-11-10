from agentforge.database.query_executor import execute_query

def test_query():

    query = """
    SELECT *
    FROM courses
    LIMIT 5
    """

    df = execute_query(query)

    print("\nQuery Result:")
    print(df)

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)


if __name__ == "__main__":
    test_query()