import pydeck as pdk
import streamlit as st

from agentforge.traffic_tool.code.location import (
    search_location,
    extract_location_details,
)
from agentforge.traffic_tool.code.routing import calculate_route


# Colors (RGB)
BEST_ROUTE_COLOR = [37, 99, 235]        # blue
ALT_ROUTE_COLOR = [148, 163, 184]       # grey
START_COLOR = [22, 163, 74]             # green
END_COLOR = [220, 38, 38]               # red


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def _pick(summary, *keys, default=0):
    """Return the first key that exists (TomTom uses different names in different APIs)."""
    for key in keys:
        if key in summary:
            return summary[key]
    return default


def _route_path(route):
    """Return the route as a list of [longitude, latitude] points, joining all legs."""
    path = []

    for leg in route.get("legs", []):
        if "path" in leg:                       # GeoJSON style: [[lon, lat], ...]
            path.extend(leg["path"]["coordinates"])
        elif "points" in leg:                   # Classic style: [{"latitude", "longitude"}, ...]
            path.extend([p["longitude"], p["latitude"]] for p in leg["points"])

    if not path:
        raise ValueError("Route geometry was not found in the TomTom response.")

    return path


def _find_location(name):
    """Search for a place and return its first valid match."""
    locations = extract_location_details(search_location(name))

    if not locations:
        raise ValueError(f"No location found for: {name}")

    return locations[0]


def _format_minutes(minutes):
    if minutes < 60:
        return f"{minutes:.0f} min"
    return f"{int(minutes // 60)} h {minutes % 60:.0f} min"


# --------------------------------------------------
# Data (cached so TomTom isn't called again on every rerun)
# --------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)
def get_routes(origin_name, destination_name):
    """Look up both places and return the routes, fastest first."""

    origin = _find_location(origin_name)
    destination = _find_location(destination_name)

    route_data = calculate_route(
        origin=origin,
        destination=destination,
        alternatives=2,
    )

    routes = []
    for route in route_data.get("routes", []):
        summary = route["summary"]
        routes.append({
            "path": _route_path(route),
            "distance_km": summary["lengthInMeters"] / 1000,
            "duration_min": _pick(summary, "travelDurationInSeconds", "travelTimeInSeconds") / 60,
            "delay_min": _pick(summary, "trafficDelayDurationInSeconds", "trafficDelayInSeconds") / 60,
        })

    routes.sort(key=lambda r: r["duration_min"])

    return {
        "origin": [float(origin["longitude"]), float(origin["latitude"])],
        "destination": [float(destination["longitude"]), float(destination["latitude"])],
        "routes": routes,
    }


# --------------------------------------------------
# UI
# --------------------------------------------------

def _build_map(data, origin_name, destination_name):
    best, *alternatives = data["routes"]

    alt_data = [
        {"path": r["path"], "name": f"Alternative {i} · {_format_minutes(r['duration_min'])}"}
        for i, r in enumerate(alternatives, start=1)
    ]
    best_data = [{"path": best["path"], "name": f"Fastest · {_format_minutes(best['duration_min'])}"}]

    markers = [
        {"position": data["origin"], "color": START_COLOR, "name": f"Start: {origin_name}"},
        {"position": data["destination"], "color": END_COLOR, "name": f"End: {destination_name}"},
    ]

    # Note: pydeck treats plain strings as data fields, so sizes are fixed in pixels
    # with min/max limits instead of width_units="pixels".
    def path_layer(rows, color, px, pickable=True):
        return pdk.Layer(
            "PathLayer",
            data=rows,
            get_path="path",
            get_color=color,
            get_width=1,
            width_min_pixels=px,
            width_max_pixels=px,
            cap_rounded=True,
            joint_rounded=True,
            pickable=pickable,
        )

    layers = [
        path_layer(alt_data, ALT_ROUTE_COLOR, 5),                     # alternatives (grey)
        path_layer(best_data, [255, 255, 255], 11, pickable=False),   # white outline
        path_layer(best_data, BEST_ROUTE_COLOR, 7),                   # fastest (blue, on top)
        pdk.Layer(
            "ScatterplotLayer",
            data=markers,
            get_position="position",
            get_fill_color="color",
            get_line_color=[255, 255, 255],
            get_radius=1,
            radius_min_pixels=9,
            radius_max_pixels=9,
            line_width_min_pixels=3,
            stroked=True,
            pickable=True,
        ),
    ]

    # Fit the map to the whole route, whatever its length
    view = pdk.data_utils.compute_view(best["path"], view_proportion=1)
    view.zoom = max(view.zoom - 0.5, 3)

    return pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_provider="carto",
        map_style=pdk.map_styles.CARTO_LIGHT,
        tooltip={"text": "{name}"},
    )


def render_traffic_map(origin_name, destination_name):

    if not origin_name or not destination_name:
        return

    try:
        with st.spinner("Calculating live traffic routes..."):
            data = get_routes(origin_name, destination_name)
    except Exception as error:
        st.error(f"Unable to load the route: {error}")
        return

    if not data["routes"]:
        st.warning("No routes found between these locations.")
        return

    best = data["routes"][0]

    # 1. Key numbers for the fastest route
    col1, col2, col3 = st.columns(3)
    col1.metric("Distance", f"{best['distance_km']:.1f} km", border=True)
    col2.metric("Travel time", _format_minutes(best["duration_min"]), border=True)
    col3.metric(
        "Traffic delay",
        _format_minutes(best["delay_min"]) if best["delay_min"] >= 1 else "None",
        border=True,
    )

    # 2. Map
    st.pydeck_chart(_build_map(data, origin_name, destination_name), height=480)
    st.caption("🔵 Fastest route  ·  ⚪ Alternatives  ·  🟢 Start  ·  🔴 End")

    # 3. Compare all routes
    if len(data["routes"]) > 1:
        st.markdown("##### Route comparison")
        rows = [
            {
                "Route": "⭐ Fastest" if i == 0 else f"Alternative {i}",
                "Distance": f"{r['distance_km']:.1f} km",
                "Travel time": _format_minutes(r["duration_min"]),
                "Traffic delay": _format_minutes(r["delay_min"]),
                "Slower by": "—" if i == 0 else _format_minutes(r["duration_min"] - best["duration_min"]),
            }
            for i, r in enumerate(data["routes"])
        ]
        st.dataframe(rows, hide_index=True)
