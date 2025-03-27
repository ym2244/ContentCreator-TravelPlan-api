from travel_map_generator import extract_locations_from_travel_plan, render_colored_map
from utils import get_google_api_key
import webbrowser

# Mock guidebook content
mock_guidebook = """
<b>User Travel Information:</b>
- <b>Name:</b> Lydia
- <b>Destination:</b> Japan
- <b>Days:</b> 4
- <b>Budget:</b> Moderate
- <b>Style:</b> Relaxed
- <b>Transportation:</b> Public Transit
- <b>User Interest:</b> Local Cuisine

<b>Travel Plan:</b>
<b>Day 1</b>  
- <b>Morning:</b> Visit Asakusa Temple  
- <b>Afternoon:</b> Explore Akihabara  
- <b>Evening:</b> Enjoy dinner in Shinjuku  
- <b>Places:</b> Asakusa Temple, Akihabara, Shinjuku

<b>Day 2</b>  
- <b>Morning:</b> Visit Arashiyama Bamboo Grove  
- <b>Afternoon:</b> Explore Nishiki Market  
- <b>Evening:</b> Enjoy kaiseki meal in Gion  
- <b>Places:</b> Arashiyama Bamboo Grove, Nishiki Market, Tokyo
"""

# Step 1: Extract structured places by day
day_places = extract_locations_from_travel_plan(mock_guidebook)

if not day_places:
    print("❌ No valid places found in travel plan.")
else:
    # Step 2: Generate HTML map with colored markers
    render_colored_map(day_places, api_key=get_google_api_key())

    # Step 3: Open the generated HTML in browser
    webbrowser.open("test_google_map_output.html")
