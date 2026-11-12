
from agentforge.traffic_tool.code.traffic import tomtom_traffic_tool

result = tomtom_traffic_tool.invoke({
    "origin": "HSR Layout, Bengaluru",
    "destination": "Electronic City, Bengaluru"
})

print(result)
