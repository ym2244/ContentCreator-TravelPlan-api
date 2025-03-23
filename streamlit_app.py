import streamlit as st
import requests

# Page configuration
st.set_page_config(page_title="AI Travel Plan Creator", layout="wide")
st.title("🌍 AI Travel Plan Creator")

API_URL = "http://127.0.0.1:8000/travel_plan_api"

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""  # Stores all previous <CHAT> lines
if "guidebook" not in st.session_state:
    st.session_state.guidebook = """<b>User Travel Guidebook:</b>
- <b>Name:</b> 
- <b>Destination:</b> 
- <b>Days:</b> 
- <b>Budget:</b> 
- <b>Style:</b> 
- <b>Transportation:</b> 

<b>Travel Plan:</b>
<b>Day 1</b>  
- <b>Morning:</b>  
- <b>Afternoon:</b>  
- <b>Evening:</b>"""  # Default guidebook template

# Sidebar input
tabs = st.sidebar.tabs(["💬 Chat Input"])
with tabs[0]:
    st.subheader("Send a message to the Travel AI")
    user_input = st.text_area("✍️ Your message:", height=150)
    system_prompt = st.text_area("⚙️ System prompt (optional):", height=100)
    send_button = st.button("🚀 Send")

# Handle user request
if send_button and user_input.strip():
    # Append user input to chat history
    new_user_line = f"USER: {user_input.strip()}"
    full_chat = f"{st.session_state.chat_history}\n{new_user_line}".strip()

    # Compose full user message (CHAT + CONTENT)
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

            # Split <CHAT> and <CONTENT>
            if "<CONTENT>" in response:
                chat_part = response.split("<CONTENT>")[0]
                chat_part = chat_part.replace("<CHAT>", "").replace("</CHAT>", "").strip()
                content_part = response.split("<CONTENT>")[1].replace("</CONTENT>", "").strip()
            else:
                chat_part = response.strip()
                content_part = st.session_state.guidebook

            # Update state
            st.session_state.chat_history += f"\nBOT: {chat_part}"
            st.session_state.guidebook = content_part
        else:
            st.error("❌ API error: " + res.text)
    except Exception as e:
        st.error("❌ Connection error: " + str(e))

# UI display
st.subheader("📝 Conversation Log")
st.text_area("Conversation", value=st.session_state.chat_history.strip(), height=300)

st.subheader("🧭 Travel Guidebook")
st.markdown(st.session_state.guidebook or "_No guidebook data yet._")
