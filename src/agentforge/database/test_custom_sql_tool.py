from agentforge.database.custom_sql_tool import execute_sql


def test_custom_sql_tool():

    query = """
    DELETE FROM employees
    WHERE department = 'IT'
    """

    result = execute_sql.invoke({
        "query": query
    })

    print("\nSQL Query Result:")
    print(result)


if __name__ == "__main__":
    test_custom_sql_tool()