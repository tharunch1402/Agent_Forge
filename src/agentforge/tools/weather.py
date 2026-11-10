from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from agentforge.config import settings
from langchain.messages import HumanMessage, AIMessage, SystemMessage
import requests

@tool
def get_weather(city:str)-> str:
    ''' Getting a temperature of a particular city in the world '''


    API_KEY = settings.WEATHER_API_KEY
    url = 'http://api.openweathermap.org/data/2.5/weather'

    params = {
        'q':city,
        'appid':API_KEY,
        'units':'metric'
        }
    temperature = requests.get(url,params = params).json()
    return f'the temperature of {city} is {temperature}'