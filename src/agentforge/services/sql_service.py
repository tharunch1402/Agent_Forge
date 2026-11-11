
import pandas as pd
from io import StringIO
from agentforge.agents import build_agent


def ask_sql_question(question: str):

    try:
        # Build AI agent
        agent = build_agent()

        # Invoke AI agent
        response = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": question
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

        # Extract SQL checker output
        validation_output = None

        for message in response["messages"]:
            if getattr(message, "name", None) == "sql_db_query_checker":
                validation_output = message.content

        # Extract SQL execution result
        query_result = None

        for message in response["messages"]:
            if getattr(message, "name", None) == "execute_sql":
                query_result = message.content



        # Determine response status
        tool_error = any(
            getattr(message, "status", None) == "error"
            for message in response["messages"]
            if getattr(message, "name", None) == "execute_sql"
        )

        if tool_error:
            status = "error"
        elif query_result is not None:
            status = "success"
        else:
            status = "no_sql"
            

        # Convert JSON string into DataFrame
        if query_result is not None:
            df = pd.read_json(
                StringIO(query_result),
                orient="split"
            )
        else:
            df = pd.DataFrame()

        # Extract final AI answer
        final_answer = response["messages"][-1].content

        # Prepare structured response
        agent_response = {
            "status": status,
            "generated_sql": generated_sql,
            "validation_output": validation_output,
            "query_result": query_result,
            "dataframe": df,
            "final_answer": final_answer
        }

        return agent_response

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


