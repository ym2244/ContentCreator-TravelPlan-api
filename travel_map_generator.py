import folium
import requests
from streamlit_folium import folium_static
import re
import streamlit as st

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
    """
    Extracts place names from all <b>Places:</b> lines in the <CONTENT> block.
    Returns a list of unique places in order of appearance.
    """
    matches = re.findall(r"<b>Places:</b>\s*(.*?)\n", travel_content)
    all_places = []
    for line in matches:
        places = [p.strip() for p in line.split(",") if p.strip()]
        all_places.extend(places)
    return list(dict.fromkeys(all_places))

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

def render_map_streamlit_if_ready(locations: list):
    if not locations:
        st.info("🗺️ Your travel map will appear here once your plan is confirmed.")
        return
    m = generate_travel_map(locations)
    if m:
        folium_static(m)
    else:
        st.warning("⚠️ Could not generate map. Check location names.")
