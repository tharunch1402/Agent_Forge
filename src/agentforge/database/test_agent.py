from agentforge.agents import build_agent
import pandas as pd
from io import StringIO
from agentforge.services.sql_service import ask_sql_question


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


    validation_output = None

    for message in response["messages"]:

        if getattr(message, "name", None) == "sql_db_query_checker":

            validation_output = message.content


    query_result = None

    for message in response['messages']:

        if getattr(message,'name',None) == 'execute_sql':

            query_result = message.content
    
    # Convert JSON string into DataFrame
    df = pd.read_json(StringIO(query_result), orient="split")
 
    final_answer = response['messages'][-1].content

    agent_response = {
        'status' : status,
        'generated_sql' : generated_sql,
        'validation_output' : validation_output,
        'query_result' : query_result,
        'dataframe' : df,
        'final_answer' : final_answer
    }

    return agent_response

def test_sql_service():

    result = ask_sql_question(
        "Find the employees from IT Department"
    )

    print("\nResponse Status:")
    print(result.get("status"))

    print("\nGenerated SQL:")
    print(result["generated_sql"])

    print("\nSQL Checker Output:")
    print(result["validation_output"])

    print("\nQuery Results:")
    print(result["dataframe"])

    print("\nFinal Answer:")
    print(result["final_answer"])


def test_sql_integration():

    questions = [
        "Find employees working in IT department",
        "Find employees working in the department named Space Research",
        "Explain what Python is and where it is used"
    ]

    for question in questions:

        print("\n" + "=" * 60)
        print("QUESTION:", question)

        result = ask_sql_question(question)

        print("\nSTATUS:", result.get("status"))
        print("\nGENERATED SQL:", result.get("generated_sql"))
        print("\nDATAFRAME:")
        print(result.get("dataframe"))
        print("\nFINAL ANSWER:")
        print(result.get("final_answer"))


if __name__ == "__main__":
    test_sql_integration()