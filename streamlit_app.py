import streamlit as st
import requests
import re
from travel_map_generator import render_colored_map, extract_locations_from_travel_plan

# Page configuration
st.set_page_config(page_title="AI Travel Plan Creator", layout="wide")
st.title("🌍 AI Travel Plan Creator")

API_URL = st.secrets["API_BASE_URL"] + "/travel_plan_api"

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""
if "latest_exchange" not in st.session_state:
    st.session_state.latest_exchange = ""
if "guidebook" not in st.session_state:
    st.session_state.guidebook = """<b>User Travel Information:</b>
- <b>Name:</b> 
- <b>Destination:</b> 
- <b>Days:</b> 
- <b>Budget:</b> 
- <b>Style:</b> 
- <b>Transportation:</b> 
- <b>User Interest:</b>
"""
if "travel_stops" not in st.session_state:
    st.session_state.travel_stops = {}
if "send_trigger" not in st.session_state:
    st.session_state.send_trigger = False

# Sidebar input
tabs = st.sidebar.tabs(["💬 Chat Input"])
with tabs[0]:
    st.subheader("Send a message to the Travel AI")

    def trigger_send():
        st.session_state.send_trigger = True

    user_input = st.text_area("✍️ Your message:", height=100, on_change=trigger_send)
    send_button = st.button("🚀 Send")

# Handle user request
if (st.session_state.send_trigger or send_button) and user_input.strip():
    st.session_state.send_trigger = False
    user_message = user_input.strip()
    new_user_line = f"USER: {user_message}"
    full_chat = f"{st.session_state.chat_history}\n{new_user_line}".strip()

    user_message_payload = f"""
<CHAT>
{full_chat}
</CHAT>

<CONTENT>
{st.session_state.guidebook.strip()}
</CONTENT>
""".strip()

    query = {
        "user_message": user_message_payload
    }

    try:
        res = requests.post(API_URL, params=query)
        if res.status_code == 200:
            result = res.json()
            response = result.get("response", "(No response)")

            if "<CONTENT>" in response:
                chat_part = response.split("<CONTENT>")[0]
                chat_part = chat_part.replace("<CHAT>", "").replace("</CHAT>", "").strip()
                content_block_match = re.search(r"<CONTENT>(.*?)</CONTENT>", response, re.DOTALL)
                content_part = content_block_match.group(1).strip() if content_block_match else st.session_state.guidebook
            else:
                chat_part = response.strip()
                content_part = st.session_state.guidebook

            # ✅ Extract last exchange only (avoid duplicating full chat)
            last_user = f"USER: {user_message.strip()}"
            bot_lines = chat_part.strip().split("BOT:")
            last_bot_response = bot_lines[-1].strip() if len(bot_lines) > 1 else chat_part.strip()
            st.session_state.latest_exchange = f"{last_user}\nBOT: {last_bot_response}"

            st.session_state.chat_history = full_chat  # Keep full history for prompt
            st.session_state.guidebook = content_part

            # 🌍 Update travel stops by day
            day_place_dict = extract_locations_from_travel_plan(content_part)
            st.session_state.travel_stops = day_place_dict

            if "Congratulations! Your full travel plan has been successfully completed" in response:
                st.success("🎉 Your travel plan is complete! Here's your final travel route:")
        else:
            st.error("❌ API error: " + res.text)
    except Exception as e:
        st.error("❌ Connection error: " + str(e))

# UI display
st.subheader("📝 Conversation Log")

scroll_style = """
<style>
#chatbox {
    height: 300px;
    overflow-y: auto;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 10px;
    background-color: #fafafa;
}
.bubble-user {
    margin: 5px 0;
    color: #333;
}
.bubble-bot {
    margin: 5px 0;
    color: #004085;
    font-weight: 500;
}
</style>
"""

chat_lines = [line.strip() for line in st.session_state.latest_exchange.strip().split("\n") if line.strip()]
html_chat = "<div id='chatbox'>"
for line in chat_lines:
    if line.startswith("USER:"):
        html_chat += f"<div class='bubble-user'>🧍 <strong>You:</strong> {line[5:].strip()}</div>"
    elif line.startswith("BOT:"):
        html_chat += f"<div class='bubble-bot'>🤖 <strong>AI:</strong> {line[4:].strip()}</div>"
html_chat += "<div id='scroll-anchor'></div></div>"
html_chat += """
<script>
  var anchor = document.getElementById("scroll-anchor");
  if (anchor) {
    anchor.scrollIntoView({ behavior: "smooth" });
  }
</script>
"""

st.markdown(scroll_style + html_chat, unsafe_allow_html=True)

# Guidebook display
st.subheader("📘 Travel Guidebook")

def split_guidebook(content: str):
    content = re.sub(
        r"(<b>User Interest:</b>.*?)(<b>Travel Plan:</b>)",
        r"\1\n\2", content, flags=re.DOTALL)
    content = re.sub(
        r"(<b>Transportation:</b>.*?)(<b>Travel Plan:</b>)",
        r"\1\n\2", content, flags=re.DOTALL)
    content = re.sub(
        r"(<b>Places:</b>.*?)(<b>Day \d+</b>)",
        r"\1\n\2", content, flags=re.DOTALL)

    parts = re.split(r"<b>Travel Plan:</b>", content)
    travel_info = parts[0].replace("<b>User Travel Information:</b>", "").strip()
    travel_plan = parts[1].strip() if len(parts) > 1 else ""

    fields = ["Name", "Destination", "Days", "Budget", "Style", "Transportation", "User Interest"]
    info_dict = {}
    for field in fields:
        match = re.search(rf"- <b>{field}:</b>(.*)", travel_info)
        info_dict[field] = match.group(1).strip() if match else ""

    fixed_info = "\n".join([f"- <b>{field}:</b> {info_dict[field]}" for field in fields])
    return fixed_info, travel_plan

travel_info, travel_plan = split_guidebook(st.session_state.guidebook)

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 🧽 Travel Information")
    if travel_info:
        st.markdown(travel_info, unsafe_allow_html=True)
    else:
        st.info("No user information yet.")
with col2:
    st.markdown("#### 🗽 Travel Plan")
    if travel_plan:
        st.markdown(travel_plan, unsafe_allow_html=True)
    else:
        st.info("Travel plan will appear here once generated.")

# Map rendering
st.subheader("📍 Travel Route Map")
render_colored_map(st.session_state.travel_stops)
