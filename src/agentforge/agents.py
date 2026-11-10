from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from agentforge.config import settings
from agentforge.tools.weather import get_weather
from agentforge.database.sql_toolkit import get_sql_tools
from agentforge.database.custom_sql_tool import execute_sql

def build_agent():

    model = ChatOpenAI(
        model=settings.MODEL,
        temperature=0,
        api_key=settings.OPENAI_API_KEY
    )
    sql_tool = get_sql_tools()

    tools = [
        get_weather,
        *sql_tool,
        execute_sql ]

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt='''
        You are a helpful AI assistant.

        You can:
        1. Provide weather information for cities worldwide.
        2. Answer questions using the MySQL database.

        When answering database questions:
        - Use SQL tools to inspect tables and schemas.
        - Generate SQL queries based on the user's question.
        - Always check SQL queries before executing them.
        - Use execute_sql to execute SELECT queries.
        - Never modify or delete database records.
        - Provide clear answers based on query results.
        - Do not invent database information.
                '''
    )

    return agent