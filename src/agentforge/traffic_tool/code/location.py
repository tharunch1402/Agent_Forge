import requests
from agentforge.config import settings
from typing import Any

BASE_URL = "https://api.tomtom.com/search/2/search/{query}.json"

def search_location(query :str, limit:int = 5)-> list[dict[str,Any]]:
    ''' Search for a location using TomTom Fuzzy search API '''

    # Validating the input
    if not isinstance(query,str) or not query.strip():
        raise ValueError("Location name cannot be empty")

    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Limit must be an integer between 1 and 100.")

    # Prepare API request
    url = BASE_URL.format(query = requests.utils.quote(query.strip()))
    params = {
        "key": settings.TOMTOM_API_KEY,
        "limit": limit,
        "countrySet": "IN",
        "typeahead": "true",
    }

    # Send API request

    try:
        response = requests.get(
            url,
            params = params,
            timeout = 10
        )

        response.raise_for_status()

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "TomTom API request timed out."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"TomTom API returned HTTP {response.status_code}."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Unable to connect to TomTom API: {exc}"
        ) from exc

    # parse the API response

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("TomTom returned an invalid JSON response.") from exc

    results = data.get("results")

    if not isinstance(results, list):
        raise RuntimeError("Unexpected response format from TomTom.")

    if not results:
        return []
    
    return results

def extract_location_details(results):
    locations = []

    for result in results:
        position = result.get("position") or {}
        address = result.get("address") or {}
        poi = result.get("poi") or {}

        latitude = position.get("lat")
        longitude = position.get("lon")

        # Skip results without valid coordinates
        if latitude is None or longitude is None:
            continue

        locations.append({
            "name": poi.get("name") or address.get("freeformAddress"),
            "address": address.get("freeformAddress"),
            "latitude": latitude,
            "longitude": longitude,
            "type": result.get("type"),
            "score": result.get("score"),
        })

    return locations

   

if __name__ == '__main__':
    result = search_location('Gachibowli')
    location = extract_location_details(result)
    print(location)