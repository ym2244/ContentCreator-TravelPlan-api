import folium
import requests
from streamlit_folium import folium_static
import re

def geocode_place(place):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={place}"
    headers = {"User-Agent": "AI Travel Planner for Lydia"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"[Geocoding Error] Place: {place} — {e}")
    return None

def extract_locations_from_travel_plan(travel_content: str):
    matches = re.findall(r'Visit\s+([A-Za-z0-9\s\-\'(),]+)', travel_content)
    return list(set(matches))  # remove duplicates

def generate_travel_map(locations):
    coords = []
    for place in locations:
        coord = geocode_place(place)
        if coord:
            coords.append((coord[0], coord[1], place))

    if not coords:
        return None

    m = folium.Map(location=coords[0][:2], zoom_start=6)

    for i, (lat, lon, name) in enumerate(coords):
        folium.Marker([lat, lon], popup=name, tooltip=f"Stop {i+1}").add_to(m)
        if i > 0:
            folium.PolyLine([coords[i - 1][:2], (lat, lon)], color="blue").add_to(m)

    return m

def render_map_streamlit_if_ready(content: str):
    locs = extract_locations_from_travel_plan(content)
    m = generate_travel_map(locs)
    if m:
        folium_static(m)
