
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

    MODEL = "gpt-4o-mini"

    # TiDB Cloud Data Service
    TIDB_QUERY_ENDPOINT = os.getenv("TIDB_QUERY_ENDPOINT")
    TIDB_PUBLIC_KEY = os.getenv("TIDB_PUBLIC_KEY")
    TIDB_PRIVATE_KEY = os.getenv("TIDB_PRIVATE_KEY")
    TIDB_DATABASE = os.getenv("TIDB_DATABASE", "agentforge_db")


settings = Settings()
