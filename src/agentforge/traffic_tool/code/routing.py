import requests
from agentforge.config import settings
from typing import Any

BASE_URL = "https://api.tomtom.com/maps/orbis/routing/routes/calculate"

def calculate_route(
    origin : dict[str,Any],
    destination : dict[str,Any],
    alternatives : int = 2
)-> dict[str,Any]:

    """Calculate a traffic-aware route between two locations."""

    # Validate input coordinates
    for name, location in [
        ("origin", origin),
        ("destination", destination)
    ]:
        if not isinstance(location, dict):
            raise ValueError(f"{name} must be a dictionary.")

        latitude = location.get("latitude")
        longitude = location.get("longitude")

        if latitude is None or longitude is None:
            raise ValueError(
                f"{name} must contain latitude and longitude."
            )

        if not isinstance(latitude, (int, float)) or isinstance(latitude, bool):
            raise ValueError(f"Invalid {name} latitude.")

        if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
            raise ValueError(f"Invalid {name} longitude.")

        if not -90 <= latitude <= 90:
            raise ValueError(f"Invalid {name} latitude range.")

        if not -180 <= longitude <= 180:
            raise ValueError(f"Invalid {name} longitude range.")

    if type(alternatives) is not int or not 0 <= alternatives <= 5:
        raise ValueError("Alternatives must be between 0 and 5.")

    # Prepare request headers
    headers = {
        "Content-Type": "application/json",
        "TomTom-Api-Version": "3",
        "TomTom-Api-Key": settings.TOMTOM_API_KEY,
        "Attributes": "routes"
    }

    # Prepare request body
    payload = {
        "routePlanningLocations": {
            "origin": {
                "type": "Point",
                "coordinates": [
                    origin["longitude"],
                    origin["latitude"]
                ]
            },
            "destination": {
                "type": "Point",
                "coordinates": [
                    destination["longitude"],
                    destination["latitude"]
                ]
            }
        },
        "routeType": "fast",
        "traffic": "live",
        "maxPathAlternativeRoutes": alternatives
    }

    # Send API request
    try:
        response = requests.post(
            BASE_URL,
            headers=headers,
            json=payload,
            timeout=20
        )

        response.raise_for_status()

    except requests.exceptions.Timeout as exc:
        raise RuntimeError("TomTom routing request timed out.") from exc

    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"TomTom Routing API returned HTTP {response.status_code}: "
            f"{response.text}"
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Unable to connect to TomTom Routing API: {exc}"
        ) from exc
    

    # Parse response
    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "TomTom returned an invalid JSON response."
        ) from exc

    routes = data.get("routes")

    if not isinstance(routes, list) or not routes:
        raise RuntimeError("TomTom did not return any valid routes.")

    return data


    

    
    
