from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from agentforge.config import settings
from agentforge.tools.weather import get_weather

def build_agent():

    model = ChatOpenAI(
        model=settings.MODEL,
        temperature=0,
        api_key=settings.OPENAI_API_KEY
    )

    tools = [get_weather]

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="You are a helpful assistant that can provide weather information for any city in the world."
    )

    return agent