from langchain_community.utilities import SQLDatabase
from agentforge.database.connection import engine

def get_database():
    db = SQLDatabase(engine)
    return db           