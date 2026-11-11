
import requests
from langchain.tools import tool
from agentforge.config import settings


@tool
def get_weather(city: str) -> str:
    """Get current weather information for a city."""

    API_KEY = settings.WEATHER_API_KEY

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        weather_data = response.json()

        temperature = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        description = weather_data["weather"][0]["description"]
        wind_speed = weather_data["wind"]["speed"]

        return (
            f"Weather in {city}:\n"
            f"Temperature: {temperature}°C\n"
            f"Feels like: {feels_like}°C\n"
            f"Humidity: {humidity}%\n"
            f"Condition: {description}\n"
            f"Wind speed: {wind_speed} m/s"
        )

    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            return f"City '{city}' was not found."
        return "Weather API returned an error."

    except requests.exceptions.RequestException:
        return "Unable to connect to the weather service."

    except (KeyError, IndexError, TypeError):
        return "Unable to process the weather information."
