import os
from dotenv import load_dotenv
load_dotenv()

class Settings:

    # API KEYS
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

    # MODEL
    MODEL = 'gpt-4o-mini'




settings = Settings()
