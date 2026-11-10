from langchain.tools import tool
from agentforge.database.query_executor import execute_query
import sqlglot

def validate_sql(query:str):
    parsed_sql = sqlglot.parse(query,read = 'mysql')

    if len(parsed_sql)!=1:
        raise ValueError("Only one SQL statement is allowed")

    if not isinstance(parsed_sql[0],sqlglot.exp.Select):
        raise ValueError('Only SELECT queries are allowed')

    return True

@tool
def execute_sql(query:str):
    ''' Execute a read only SQL query and return the results '''
    
    validate_sql(query)

    result = execute_query(query)

    return result.to_json(orient = 'split')
