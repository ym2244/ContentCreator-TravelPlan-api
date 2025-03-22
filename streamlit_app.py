import streamlit as st
import requests

# Configure the page layout and title
st.set_page_config(page_title="AI Travel Plan Creator", layout="wide")
st.title("🌍 AI Travel Plan Creator")

API_URL = "http://127.0.0.1:8000/travel_plan_api"

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""
if "profile" not in st.session_state:
    st.session_state.profile = ""

# Sidebar: Input section for user message and system prompt
tabs = st.sidebar.tabs(["💬 Chat Input"])
with tabs[0]:
    st.subheader("Send a message to the Travel AI")
    user_input = st.text_area("✍️ Your message:", height=150)
    system_prompt = st.text_area("⚙️ System prompt (optional):", height=100)
    send_button = st.button("🚀 Send")

# Handle API request when user clicks "Send"
if send_button and user_input.strip():
    query = {
        "user_message": user_input,
        "system_prompt": system_prompt.strip() if system_prompt.strip() else None
    }
    try:
        res = requests.post(API_URL, params=query)
        if res.status_code == 200:
            result = res.json()
            response = result.get("response", "(No response)")

            # Split response into conversation and profile parts
            chat_part = response.split("<CONTENT>")[0].replace("<CHAT>", "").replace("</CHAT>", "").strip()
            content_part = response.split("<CONTENT>")[-1].replace("</CONTENT>", "").strip()

            # Update session state
            st.session_state.chat_history += f"\n\nUSER: {user_input}\nBOT: {chat_part}"
            st.session_state.profile = content_part
        else:
            st.error("❌ API error: " + res.text)
    except Exception as e:
        st.error("❌ Connection error: " + str(e))

# Main column: Display the conversation history
st.subheader("📝 Conversation Log")
st.text_area("Conversation", value=st.session_state.chat_history, height=300)

# Right column: Display the structured travel profile
st.subheader("🧭 Travel Profile")
st.markdown(st.session_state.profile or "_No profile data yet._")
