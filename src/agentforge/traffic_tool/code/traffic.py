
from langchain.tools import tool

from agentforge.traffic_tool.code.location import (
    search_location,
    extract_location_details
)

from agentforge.traffic_tool.code.routing import calculate_route


def analyze_traffic(route):

    traffic_events = route.get("sections", {}).get("traffic", [])

    report = {
        "total_events": len(traffic_events),
        "jams": 0,
        "roadworks": 0,
        "accidents": 0,
        "other_events": 0,
        "minor": 0,
        "moderate": 0,
        "major": 0
    }

    for event in traffic_events:

        category = event.get("iconCategory", "unknown")
        severity = event.get("delayMagnitude", "unknown")

        if category == "jam":
            report["jams"] += 1
        elif category == "roadWorks":
            report["roadworks"] += 1
        elif category == "accident":
            report["accidents"] += 1
        else:
            report["other_events"] += 1

        if severity in ("minor", "moderate", "major"):
            report[severity] += 1

    if report["major"] >= 2:
        condition = "Severe"
    elif report["major"] == 1:
        condition = "Heavy"
    elif report["moderate"] >= 1:
        condition = "Moderate"
    else:
        condition = "Low"

    report["overall_condition"] = condition

    return report


def generate_recommendation(condition):

    if condition == "Severe":
        return "Avoid this route if a suitable alternative is available."

    elif condition == "Heavy":
        return "Expect significant traffic. Consider an alternative."

    elif condition == "Moderate":
        return "Allow some extra travel time."

    return "Traffic conditions appear favourable."


@tool
def tomtom_traffic_tool(origin: str, destination: str) -> str:
    """
    Find routes between two locations using TomTom.
    Compare travel times, analyze traffic conditions,
    and recommend the fastest route.

    Args:
        origin: Starting location.
        destination: Destination location.
    """

    try:

        # STEP 1: GEOCODING

        origin_results = search_location(origin)
        origin_details = extract_location_details(origin_results)

        if not origin_details:
            return f"Could not find origin: {origin}"

        destination_results = search_location(destination)
        destination_details = extract_location_details(destination_results)

        if not destination_details:
            return f"Could not find destination: {destination}"

        origin_coordinates = origin_details[0]
        destination_coordinates = destination_details[0]


        # STEP 2: ROUTING

        route_data = calculate_route(
            origin=origin_coordinates,
            destination=destination_coordinates,
            alternatives=2
        )

        routes = route_data.get("routes", [])

        if not routes:
            return "No routes found for the given locations."


        # STEP 3: FIND FASTEST ROUTE

        fastest_route = min(
            routes,
            key=lambda route: route["summary"]["travelDurationInSeconds"]
        )

        fastest_summary = fastest_route["summary"]


        # STEP 4: ANALYZE ALL ROUTES

        result = []

        result.append(f"Origin: {origin}")
        result.append(f"Destination: {destination}")
        result.append(f"\nAvailable routes: {len(routes)}")

        for i, route in enumerate(routes, start=1):

            summary = route["summary"]
            report = analyze_traffic(route)

            distance = summary["lengthInMeters"] / 1000
            duration = summary["travelDurationInSeconds"] / 60
            delay = summary["trafficDelayDurationInSeconds"] / 60

            recommendation = generate_recommendation(
                report["overall_condition"]
            )

            result.append(f"\n--- ROUTE {i} ---")
            result.append(f"Distance: {distance:.2f} km")
            result.append(f"Travel time: {duration:.2f} minutes")
            result.append(f"Traffic delay: {delay:.2f} minutes")
            result.append(f"Traffic condition: {report['overall_condition']}")
            result.append(f"Traffic events: {report['total_events']}")
            result.append(f"Jams: {report['jams']}")
            result.append(f"Roadworks: {report['roadworks']}")
            result.append(f"Accidents: {report['accidents']}")
            result.append(f"Minor: {report['minor']}")
            result.append(f"Moderate: {report['moderate']}")
            result.append(f"Major: {report['major']}")
            result.append(f"Suggestion: {recommendation}")


        # STEP 5: RECOMMENDED ROUTE

        result.append("\n===== FASTEST ROUTE RECOMMENDATION =====")
        result.append(
            f"Distance: {fastest_summary['lengthInMeters'] / 1000:.2f} km"
        )
        result.append(
            f"Travel time: {fastest_summary['travelDurationInSeconds'] / 60:.2f} minutes"
        )
        result.append(
            f"Traffic delay: {fastest_summary['trafficDelayDurationInSeconds'] / 60:.2f} minutes"
        )

        return "\n".join(result)

    except Exception as e:
        return f"Traffic tool error: {str(e)}"
