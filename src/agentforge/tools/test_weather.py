
from agentforge.tools.weather import get_weather
from agentforge.agents import build_agent


def test_weather():

    city = "asdferhtwfegergsfeedewfefwe"

    result = get_weather.invoke({
        "city": city
    })

    print("\nWeather API Response:")
    print(result)




def test_weather_agent():

    questions = [
    "Find employees working in IT department",
    "What is the current weather in Hyderabad?"
]

    agent = build_agent()

    for question in questions:
        response = agent.invoke({
            "messages": [
                {"role": "user", "content": question}
            ]
        })

        print("\nQUESTION:", question)
        print("\nANSWER:", response["messages"][-1].content)

if __name__ == "__main__":
    test_weather_agent()

