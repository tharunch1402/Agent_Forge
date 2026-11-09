from agentforge.agents import build_agent

agent = build_agent()

response = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What is the temperature in Jam Gwang, PK ?"
        }
    ]
})

print(response['messages'][-1].content)