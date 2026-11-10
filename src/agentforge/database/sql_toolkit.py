from langchain_community.agent_toolkits import SQLDatabaseToolkit
from agentforge.database.sql_database import get_database
from langchain_openai import ChatOpenAI
from agentforge.config import settings

def get_sql_tools():

    db = get_database()
    llm = ChatOpenAI(
        model = settings.MODEL,
        api_key = settings.OPENAI_API_KEY,
        temperature = 0
    )

    toolkit = SQLDatabaseToolkit(
        db = db,
        llm = llm
    )

    tools = toolkit.get_tools()

    tools = [tool for tool in tools if tool.name!= 'sql_db_query']

    return tools

    