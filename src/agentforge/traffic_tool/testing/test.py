
from agentforge.traffic_tool.code.location import (
    search_location,
    extract_location_details
)

from agentforge.traffic_tool.code.routing import calculate_route



def analyze_traffic(route):

    sections = route.get("sections", {})
    traffic_events = sections.get("traffic", [])

    traffic_report = {
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

        severity = event.get("delayMagnitude", "unknown")

        if severity in traffic_report:
            traffic_report[severity] += 1

        category = event.get("iconCategory", "unknown")

        if category == "jam":
            traffic_report["jams"] += 1

        elif category == "roadWorks":
            traffic_report["roadworks"] += 1

        elif category == "accident":
            traffic_report["accidents"] += 1

        else:
            traffic_report["other_events"] += 1
    
    # STEP 9: OVERALL TRAFFIC CONDITION

    if traffic_report["major"] >= 2:
        condition = "Severe"

    elif traffic_report["major"] == 1:
        condition = "Heavy"

    elif traffic_report["moderate"] >= 1:
        condition = "Moderate"

    else:
        condition = "Low"

    traffic_report["overall_condition"] = condition


    return traffic_report


def generate_recommendation(route, report):

    summary = route["summary"]

    duration = summary["travelDurationInSeconds"] / 60
    delay = summary["trafficDelayDurationInSeconds"] / 60

    condition = report["overall_condition"]

    if condition == "Severe":
        recommendation = "Avoid this route if a suitable alternative is available."

    elif condition == "Heavy":
        recommendation = "Expect significant traffic. Consider an alternative route."

    elif condition == "Moderate":
        recommendation = "Allow some extra travel time."

    else:
        recommendation = "Traffic conditions appear favourable."

    return {
        "travel_time": duration,
        "traffic_delay": delay,
        "condition": condition,
        "recommendation": recommendation
    }


def test_traffic_agent():

    # ==================================
    # STEP 1: SEARCH ORIGIN
    # ==================================

    origin_results = search_location("HSR layout, Bengaluru")

    origin_details = extract_location_details(origin_results)

    if not origin_details:
        print("Origin location not found!")
        return

    origin = origin_details[0]


    # ==================================
    # STEP 2: SEARCH DESTINATION
    # ==================================

    destination_results = search_location("Electronic City, Bengaluru")

    destination_details = extract_location_details(destination_results)

    if not destination_details:
        print("Destination location not found!")
        return

    destination = destination_details[0]


    # ==================================
    # STEP 3: CALCULATE ROUTES
    # ==================================

    route_data = calculate_route(
        origin=origin,
        destination=destination,
        alternatives=2
    )

    routes = route_data.get("routes", [])

    if not routes:
        print("No routes found!")
        return


    # ==================================
    # STEP 4: DISPLAY ALL ROUTES
    # ==================================

    print("\n========== AVAILABLE ROUTES ==========")

    for i, route in enumerate(routes, start=1):

        summary = route["summary"]

        distance = summary["lengthInMeters"]
        duration = summary["travelDurationInSeconds"]
        delay = summary["trafficDelayDurationInSeconds"]

        coordinates = route["legs"][0]["path"]["coordinates"]

        print(f"\n---------- ROUTE {i} ----------")

        print(f"Distance       : {distance / 1000:.2f} km")
        print(f"Travel Time    : {duration / 60:.2f} minutes")
        print(f"Traffic Delay  : {delay / 60:.2f} minutes")
        print(f"Coordinates    : {len(coordinates)} points")


    # ==================================
    # STEP 5: FIND FASTEST ROUTE
    # ==================================

    fastest_route = min(
        routes,
        key=lambda route: route["summary"]["travelDurationInSeconds"]
    )

    fastest_summary = fastest_route["summary"]


    # ==================================
    # STEP 6: DISPLAY FASTEST ROUTE
    # ==================================

    fastest_distance = fastest_summary["lengthInMeters"]
    fastest_duration = fastest_summary["travelDurationInSeconds"]
    fastest_delay = fastest_summary["trafficDelayDurationInSeconds"]

    print("\n========== RECOMMENDED ROUTE ==========")

    print(f"Distance       : {fastest_distance / 1000:.2f} km")
    print(f"Travel Time    : {fastest_duration / 60:.2f} minutes")
    print(f"Traffic Delay  : {fastest_delay / 60:.2f} minutes")

    print("\nRecommended route selected successfully!")

    # ==================================
    # STEP 7: INSPECT TRAFFIC INFORMATION
    # ==================================

    for i, route in enumerate(route_data["routes"], start=1):

        print(f"\n========== ROUTE {i} TRAFFIC ==========")

        # Get sections from the route
        sections = route.get("sections", {})

        # Get traffic events
        traffic_sections = sections.get("traffic", [])

        if not traffic_sections:
            print("No traffic events reported for this route.")
            continue

        # Display each traffic event
        for event_number, event in enumerate(traffic_sections, start=1):

            category = event.get("iconCategory", "Unknown")
            severity = event.get("delayMagnitude", "Unknown")
            delay = event.get("delayDurationInSeconds", 0)
            speed = event.get("effectiveSpeedInKilometersPerHour", "N/A")

            print(f"\nTraffic Event {event_number}")
            print(f"Category : {category}")
            print(f"Severity : {severity}")
            print(f"Delay    : {delay} seconds")
            print(f"Speed    : {speed} km/h")
 

    
    # STEP 8: TRAFFIC ANALYSIS

    print("\n========== TRAFFIC ANALYSIS ==========")

    for i, route in enumerate(routes, start=1):

        report = analyze_traffic(route)

        print(f"\n========== ROUTE {i} ANALYSIS ==========")

        print(f"Total Events : {report['total_events']}")
        print(f"Traffic Jams : {report['jams']}")
        print(f"Roadworks    : {report['roadworks']}")
        print(f"Accidents    : {report['accidents']}")
        print(f"Other Events : {report['other_events']}")
        print(f"Minor Events    : {report['minor']}")
        print(f"Moderate Events : {report['moderate']}")
        print(f"Major Events    : {report['major']}")
        print(f"Overall Condition : {report['overall_condition']}")


    # STEP 10: ROUTE COMPARISON

    print("\n========== ROUTE COMPARISON ==========")

    for i, route in enumerate(routes, start=1):

        report = analyze_traffic(route)
        result = generate_recommendation(route, report)

        print(f"\nRoute {i}")
        print(f"Travel Time : {result['travel_time']:.2f} minutes")
        print(f"Traffic     : {result['condition']}")
        print(f"Delay       : {result['traffic_delay']:.2f} minutes")

if __name__ == "__main__":
    test_traffic_agent()
