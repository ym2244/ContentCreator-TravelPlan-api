import requests
import re
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
from utils import get_google_api_key

def extract_locations_from_travel_plan(content: str):
    matches = re.findall(r"<b>Places:</b>\s*(.*?)\n", content)
    all_places = []
    for line in matches:
        places = [p.strip() for p in line.split(",") if p.strip()]
        all_places.extend(places)
    return list(dict.fromkeys(all_places))

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
            name = top["name"]
            rating = top.get("rating", "N/A")
            return f"{name} (⭐ {rating})"
    except:
        pass
    return "Try local cuisine nearby!"

def generate_travel_map(locations, api_key=None, save_as_html=False, html_file="test_google_map_output.html"):
    if not api_key:
        api_key = get_google_api_key()
    if not api_key:
        print("❌ No Google Maps API key found.")
        return []

    coords = []
    for place in locations:
        coord = geocode_place(place, api_key)
        if coord:
            coords.append((place, coord[0], coord[1]))
        else:
            print(f"❌ Failed to geocode '{place}'")

    if not coords or not save_as_html:
        return coords

    center_lat, center_lng = coords[0][1], coords[0][2]

    markers_js = ""
    for i, (name, lat, lng) in enumerate(coords):
        rec = get_top_restaurant_nearby(lat, lng, api_key)
        # 🧠 Clean HTML: remove blank lines
        info_html = f"<div><strong>Stop {i+1}:</strong> {name}<br>🍜 Recommended: {rec}</div>".replace("\n", "").strip()
        markers_js += f"""
        const marker{i} = new google.maps.Marker({{
            position: {{ lat: {lat}, lng: {lng} }},
            map: map,
            label: "{i+1}",
            title: "Stop {i+1}: {name}"
        }});
        const info{i} = new google.maps.InfoWindow({{
            content: `{info_html}`
        }});
        marker{i}.addListener("click", () => {{
            map.setZoom(15);
            map.setCenter(marker{i}.getPosition());
            info{i}.open(map, marker{i});
        }});\n
        """

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
          {markers_js}
        }}
      </script>
    </head>
    <body onload="initMap()">
      <div id="map"></div>
    </body>
    </html>
    """

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_code)
    print(f"✅ HTML map saved to {html_file}")

    return coords

def render_map_streamlit_if_ready(locations):
    api_key = get_google_api_key()
    coords = generate_travel_map(locations, api_key=api_key, save_as_html=True)
    if not coords:
        st.warning("⚠️ Could not generate map.")
        return
    with open("test_google_map_output.html", "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=600)
