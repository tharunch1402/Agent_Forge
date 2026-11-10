from agentforge.database.sql_database import get_database

def get_tables():

    db = get_database()
    tables = db.get_usable_table_names()
    print(f'tables: {tables}')  

def get_schema():

    db = get_database()
    schema = db.get_table_info()
    print(f'schema: {schema}')

def execute_query():

    db = get_database()
    query = '''
    Select * from students
    where marks = 80
    '''
    result = db.run(query)
    print("Query Result")
    print(result)

if __name__ == "__main__":
    get_tables()
    get_schema()    
    execute_query()            