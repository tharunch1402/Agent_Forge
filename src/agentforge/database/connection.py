import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from sqlalchemy import text,create_engine

load_dotenv()

connection_url = URL.create(
    drivername = "mysql+pymysql",
    username = os.getenv("MYSQL_USER"),
    password = os.getenv("MYSQL_PASSWORD"),
    host = os.getenv("MYSQL_HOST"),
    port = int(os.getenv("MYSQL_PORT",3306)),
    database = os.getenv("MYSQL_DATABASE")
)

engine = create_engine(
    connection_url,
    pool_pre_ping = True
    )


def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print('**SUCCESSFULLY CONNECTED**')
            print(f'test_result : {result.scalar()}')
    
    except Exception as e:
        print("Database not connected ", e)