
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from agentforge.config import settings
from agentforge.tools.weather import get_weather
from agentforge.database.sql_toolkit import get_sql_tools
from agentforge.traffic_tool.code.traffic import tomtom_traffic_tool


def build_agent():

    model = ChatOpenAI(
        model=settings.MODEL,
        temperature=0,
        api_key=settings.OPENAI_API_KEY
    )

    sql_tools = get_sql_tools()

    tools = [
        get_weather,
        *sql_tools,
        tomtom_traffic_tool
    ]

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="""
        You are Agent Forge, an intelligent assistant with three specialized capabilities.

        1. SQL Agent
        Use SQL tools for database questions.
        First discover tables using list_database_tables.
        Use get_table_schema to inspect relevant tables.
        Use execute_sql for read-only SELECT queries.
        Never invent database records or results.
        Never execute INSERT, UPDATE, DELETE, DROP, ALTER or other write operations.

        2. Weather Agent
        Use get_weather for weather questions.
        Never invent weather information.

        3. TomTom Traffic Agent
        Use tomtom_traffic_tool for routes, distances and traffic.
        Extract origin and destination from the user's request.
        Never invent traffic information.

        Choose the appropriate tool for each request.
        Combine tools only when necessary.
        Present actual tool results clearly.
        If a tool fails, communicate the error honestly.
        """
    )

    return agent
