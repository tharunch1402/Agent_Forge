from agentforge.agents import build_agent

import ast

agent = build_agent()

def weather():
    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": "What is the temperature in Jam Gwang, PK ?"
            }
        ]
    })

    print(response['messages'][-1].content)




def test_sql_agent():

    agent = build_agent()

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": "Find the employees who are in 'IT' department"
            }
        ]
    })

    generated_sql = None
    # Iterate through agent messages
    for message in response["messages"]:

        # Check AI message tool calls
        tool_calls = getattr(message, "tool_calls", [])
        for tool_call in tool_calls:
            # Identify SQL checker tool
            if tool_call["name"] == "sql_db_query_checker":
                # Extract SQL query
                generated_sql = tool_call["args"]["query"]
    
    # Store SQL checker response
    validation_output = None
    # Iterate through agent messages
    for message in response["messages"]:
        if getattr(message, "name", None) == "sql_db_query_checker":
            validation_output = message.content


    # Store database query result
    query_result = None
    # Iterate through agent messages
    for message in response["messages"]:
        if getattr(message, "name", None) == "sql_db_query":
            query_result = message.content


    # Get final AI answer
    final_answer = response["messages"][-1].content

    # Combine everything into one dictionary
    agent_response = {
        "generated_sql": generated_sql,
        "validation_output": validation_output,
        "query_result": query_result,
        "final_answer": final_answer
        }

    # Convert query result string into Python data
    structured_data = ast.literal_eval(
        agent_response["query_result"]
        )
    print("\nStructured Query Result:")
    print(structured_data)

    print("\nData Type:")
    print(type(structured_data))
    print("\nComplete Agent Response:")
    print(agent_response)


if __name__ == "__main__":
    test_sql_agent()