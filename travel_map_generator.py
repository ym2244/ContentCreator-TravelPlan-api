import requests
import re
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
from utils import get_google_api_key

def extract_locations_from_travel_plan(content: str):
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

    locations = []
    marker_index = 1
    for i, (day, places) in enumerate(day_place_dict.items()):
        color_url = color_list[i % len(color_list)]
        for place in places:
            coord = geocode_place(place, api_key)
            if coord:
                lat, lng = coord
                rec = get_top_restaurant_nearby(lat, lng, api_key)
                locations.append({
                    "id": f"m{marker_index}",
                    "day": day,
                    "name": place,
                    "lat": lat,
                    "lng": lng,
                    "info": f"🍜 {rec}",
                    "color": color_url
                })
                marker_index += 1

    if not locations:
        st.warning("⚠️ No valid coordinates found.")
        return

    center_lat, center_lng = locations[0]["lat"], locations[0]["lng"]

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Travel Map</title>
      <meta charset="utf-8">
      <style>
        body {{ margin: 0; padding: 0; display: flex; }}
        #sidebar {{ width: 280px; background: #f9f9f9; padding: 16px; overflow-y: auto; border-right: 1px solid #ccc; font-family: sans-serif; font-size: 14px; }}
        #sidebar h3 {{ margin-top: 16px; color: #333; }}
        .place-link {{ cursor: pointer; color: #0066cc; margin: 6px 0; display: block; text-decoration: underline; }}
        #map {{ height: 100vh; flex: 1; }}
      </style>
      <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=places"></script>
      <script>
        let map;
        const markers = {{}};
        const infos = {{}};
        const locations = {locations};

        function initMap() {{
          if (!locations.length) return;
          map = new google.maps.Map(document.getElementById('map'), {{
            zoom: 6,
            center: {{ lat: locations[0].lat, lng: locations[0].lng }}
          }});

          const sidebar = document.getElementById("sidebar");
          let currentDay = "";

          locations.forEach((loc, index) => {{
            const position = {{ lat: loc.lat, lng: loc.lng }};
            const marker = new google.maps.Marker({{
              position,
              map,
              title: `${{loc.day}} - ${{loc.name}}`,
              icon: loc.color
            }});
            const info = new google.maps.InfoWindow({{
              content: `<strong>${{loc.day}} - ${{loc.name}}</strong><br>${{loc.info || ''}}`
            }});

            marker.addListener("click", () => {{
              map.setZoom(15);
              map.setCenter(marker.getPosition());
              info.open(map, marker);
            }});

            markers[loc.id] = marker;
            infos[loc.id] = info;

            if (loc.day !== currentDay) {{
              const dayHeader = document.createElement("h3");
              dayHeader.textContent = loc.day;
              sidebar.appendChild(dayHeader);
              currentDay = loc.day;
            }}

            const link = document.createElement("span");
            link.textContent = `• ${{loc.name}}`;
            link.className = "place-link";
            link.onclick = () => {{
              map.setZoom(15);
              map.setCenter(marker.getPosition());
              info.open(map, marker);
            }};
            sidebar.appendChild(link);
          }});
        }}
      </script>
    </head>
    <body onload="initMap()">
      <div id="sidebar"></div>
      <div id="map"></div>
    </body>
    </html>
    """

    with open("test_google_map_output.html", "w", encoding="utf-8") as f:
        f.write(html_code)
    with open("test_google_map_output.html", "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=600)
