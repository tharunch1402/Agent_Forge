from agentforge.database.sql_toolkit import get_sql_tools

def test_tools():
    tools = get_sql_tools()

    for tool in tools:
        print(f'tool_name : {tool.name}')
        print(f'tool_description : {tool.description}')
        print('=='*35)


if __name__ == '__main__':
    test_tools()