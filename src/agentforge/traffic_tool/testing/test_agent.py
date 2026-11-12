
from agentforge.agents import build_agent

agent = build_agent()

response = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "Find the fastest route from HSR Layout, Bengaluru to Electronic City, Bengaluru"
        }
    ]
})

print(response["messages"][-1].content)
