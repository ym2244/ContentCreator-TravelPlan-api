import requests
import re
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
from utils import get_google_api_key

def extract_locations_from_travel_plan(content: str):
    """
    Extract places from daily plan:
    {
        "Day 1": [...],
        "Day 2": [...],
        ...
    }
    """
    day_sections = re.findall(r"<b>Day \d+</b>.*?(?=<b>Day \d+</b>|$)", content, re.DOTALL)
    day_place_dict = {}

    for section in day_sections:
        day_match = re.search(r"<b>Day (\d+)</b>", section)
        places_match = re.search(r"<b>Places:</b>\s*(.*?)(?:<b>|$)", section, re.DOTALL)
        if day_match and places_match:
            day = f"Day {day_match.group(1)}"
            places_raw = places_match.group(1).strip()
            places_list = [p.strip() for p in places_raw.split(",") if p.strip()]
            day_place_dict[day] = places_list

    return day_place_dict


def geocode_place(place, api_key=None):
    if not api_key:
        return None
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(place)}&key={api_key}"
    try:
        res = requests.get(url)
        data = res.json()
        if data["status"] == "OK":
            loc = data["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
    except:
        pass
    return None

def get_top_restaurant_nearby(lat, lng, api_key=None):
    if not api_key:
        return "Try local cuisine nearby!"
    nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=800&type=restaurant&key={api_key}"
    try:
        res = requests.get(nearby_url)
        data = res.json()
        if data["status"] == "OK" and data["results"]:
            top = sorted(data["results"], key=lambda x: x.get("rating", 0), reverse=True)[0]
            return f"{top['name']} (⭐ {top.get('rating', 'N/A')})"
    except:
        pass
    return "Try local cuisine nearby!"

def render_colored_map(day_place_dict, api_key=None):
    if not api_key:
        api_key = get_google_api_key()
    if not api_key:
        st.warning("❌ No Google Maps API key found.")
        return

    color_list = [
        "http://maps.google.com/mapfiles/ms/icons/red-dot.png",
        "http://maps.google.com/mapfiles/ms/icons/blue-dot.png",
        "http://maps.google.com/mapfiles/ms/icons/green-dot.png",
        "http://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
        "http://maps.google.com/mapfiles/ms/icons/purple-dot.png",
        "http://maps.google.com/mapfiles/ms/icons/orange-dot.png",
        "http://maps.google.com/mapfiles/ms/icons/pink-dot.png",
    ]

    coords = []
    marker_js_blocks = []
    marker_index = 1
    for i, (day, places) in enumerate(day_place_dict.items()):
        color_url = color_list[i % len(color_list)]
        for place in places:
            coord = geocode_place(place, api_key)
            if coord:
                lat, lng = coord
                rec = get_top_restaurant_nearby(lat, lng, api_key)
                info_html = f"<div><strong>{day} - Stop {marker_index}:</strong> {place}<br>🍜 Recommended: {rec}</div>".replace("\n", "").strip()
                js_block = f"""
                const marker{marker_index} = new google.maps.Marker({{
                    position: {{ lat: {lat}, lng: {lng} }},
                    map: map,
                    icon: "{color_url}",
                    title: "{day} - Stop {marker_index}: {place}"
                }});
                const info{marker_index} = new google.maps.InfoWindow({{
                    content: `{info_html}`
                }});
                marker{marker_index}.addListener("click", () => {{
                    map.setZoom(15);
                    map.setCenter(marker{marker_index}.getPosition());
                    info{marker_index}.open(map, marker{marker_index});
                }});\n
                """
                marker_js_blocks.append(js_block)
                coords.append((lat, lng))
                marker_index += 1

    if not coords:
        st.warning("⚠️ No valid coordinates found.")
        return

    center_lat, center_lng = coords[0]
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Travel Map</title>
      <meta charset="utf-8">
      <style>#map {{ height: 100vh; width: 100%; }}</style>
      <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=places"></script>
      <script>
        function initMap() {{
          if (typeof google === 'undefined') {{
            document.getElementById('map').innerHTML = '❌ Google Maps failed to load. Check your API key.';
            return;
          }}
          const map = new google.maps.Map(document.getElementById('map'), {{
            zoom: 6,
            center: {{ lat: {center_lat}, lng: {center_lng} }}
          }});
          {"".join(marker_js_blocks)}
        }}
      </script>
    </head>
    <body onload="initMap()">
      <div id="map"></div>
    </body>
    </html>
    """

    with open("test_google_map_output.html", "w", encoding="utf-8") as f:
        f.write(html_code)
    with open("test_google_map_output.html", "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=600)
