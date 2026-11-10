from agentforge.agents import build_agent


def test_sql_agent():

    agent = build_agent()

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": "Find employees working in IT department"
            }
        ]
    })

    # Extract generated SQL
    generated_sql = None

    for message in response["messages"]:

        tool_calls = getattr(message, "tool_calls", [])

        for tool_call in tool_calls:

            if tool_call["name"] == "sql_db_query_checker":

                generated_sql = tool_call["args"]["query"]

    print("\nGenerated SQL:")
    print(generated_sql)


    validation_output = None

    for message in response["messages"]:

        if getattr(message, "name", None) == "sql_db_query_checker":

            validation_output = message.content


    print("\nSQL Checker Output:")
    print(validation_output)

if __name__ == "__main__":
    test_sql_agent()