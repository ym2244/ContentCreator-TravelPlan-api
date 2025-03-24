import streamlit as st
import requests
import re
from travel_map_generator import render_map_streamlit_if_ready, extract_locations_from_travel_plan

# Page configuration
st.set_page_config(page_title="AI Travel Plan Creator", layout="wide")
st.title("🌍 AI Travel Plan Creator")

API_URL = "http://127.0.0.1:8000/travel_plan_api"

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""
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
    st.session_state.travel_stops = []

# Sidebar input
tabs = st.sidebar.tabs(["💬 Chat Input"])
with tabs[0]:
    st.subheader("Send a message to the Travel AI")
    user_input = st.text_area("✍️ Your message:", height=150)
    system_prompt = st.text_area("⚙️ System prompt (optional):", height=100)
    send_button = st.button("🚀 Send")

# Handle user request
if send_button and user_input.strip():
    new_user_line = f"USER: {user_input.strip()}"
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
        "user_message": user_message_payload,
        "system_prompt": system_prompt.strip() if system_prompt.strip() else None
    }

    try:
        res = requests.post(API_URL, params=query)
        if res.status_code == 200:
            result = res.json()
            response = result.get("response", "(No response)")

            if "<CONTENT>" in response:
                chat_part = response.split("<CONTENT>")[0]
                chat_part = chat_part.replace("<CHAT>", "").replace("</CHAT>", "").strip()

                # Intercept the part between <CONTENT> and </CONTENT> (avoid reading redundant content)
                content_block_match = re.search(r"<CONTENT>(.*?)</CONTENT>", response, re.DOTALL)
                content_part = content_block_match.group(1).strip() if content_block_match else st.session_state.guidebook
            else:
                chat_part = response.strip()
                content_part = st.session_state.guidebook

            st.session_state.chat_history += f"\nBOT: {chat_part}"
            st.session_state.guidebook = content_part

            # Update travel stops each time content updates
            new_stops = extract_locations_from_travel_plan(content_part)
            st.session_state.travel_stops = new_stops

            # Final wrap-up & visual map
            if "Congratulations! Your full travel plan has been successfully completed" in response:
                st.success("🎉 Your travel plan is complete! Here's your final travel route:")

        else:
            st.error("❌ API error: " + res.text)
    except Exception as e:
        st.error("❌ Connection error: " + str(e))

# UI display
st.subheader("📝 Conversation Log")
st.text_area("Conversation", value=st.session_state.chat_history.strip(), height=300)

# ---------------------------
# ✅ Smart Guidebook Display
# ---------------------------
st.subheader("📘 Travel Guidebook")

def split_guidebook(content: str):
    # 🔧 Fix line break errors
    content = re.sub(
        r"(<b>User Interest:</b>.*?)(<b>Travel Plan:</b>)",
        r"\1\n\2", content, flags=re.DOTALL)
    content = re.sub(
        r"(<b>Transportation:</b>.*?)(<b>Travel Plan:</b>)",
        r"\1\n\2", content, flags=re.DOTALL)
    content = re.sub(
        r"(<b>Places:</b>.*?)(<b>Day \d+</b>)",
        r"\1\n\2", content, flags=re.DOTALL)

    # ✂️ Split the Travel Plan and Travel Information parts
    parts = re.split(r"<b>Travel Plan:</b>", content)
    travel_info = parts[0].replace("<b>User Travel Information:</b>", "").strip()
    travel_plan = parts[1].strip() if len(parts) > 1 else ""

    # ✅ Standard Field Population
    fields = [
        "Name", "Destination", "Days", "Budget", "Style", "Transportation", "User Interest"
    ]
    info_dict = {}
    for field in fields:
        match = re.search(rf"- <b>{field}:</b>(.*)", travel_info)
        info_dict[field] = match.group(1).strip() if match else ""

    # 🔧 Regenerate the reorganized travel_info (make sure all fields are complete and in the correct order)
    fixed_info = "\n".join(
        [f"- <b>{field}:</b> {info_dict[field]}" for field in fields]
    )

    return fixed_info, travel_plan


travel_info, travel_plan = split_guidebook(st.session_state.guidebook)

# Two-column display
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

# Optional route map
st.subheader("📍 Travel Route Map")
render_map_streamlit_if_ready(st.session_state.travel_stops)
