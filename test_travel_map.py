# test_travel_map.py

from travel_map_generator import extract_locations_from_travel_plan, generate_travel_map

# ✅ 模拟 Guidebook 内容
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

<b>Day 2</b>  
- <b>Morning:</b> Visit Arashiyama Bamboo Grove  
- <b>Afternoon:</b> Explore Nishiki Market  
- <b>Evening:</b> Enjoy kaiseki meal in Gion
"""

# ✅ 提取地点名
places = extract_locations_from_travel_plan(mock_guidebook)
print("Extracted places:", places)

# ✅ 生成地图
m = generate_travel_map(places)

# ✅ 保存为 HTML 文件（可在浏览器打开）
if m:
    m.save("test_travel_route_map.html")
    print("✅ Map generated successfully! Open 'test_travel_route_map.html' to view it.")
else:
    print("⚠️ Could not generate map. Please check if valid places were found.")
