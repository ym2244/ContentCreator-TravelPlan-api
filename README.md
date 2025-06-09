# 🌍 Content Creator Chat – Travel Plan API

This project is part of the **Content Creator Chat** platform, providing an intelligent, multi-agent travel planner built with **FastAPI + Streamlit**. It interacts with users through structured prompts and generates personalized daily travel plans using LLMs from Groq (LLaMA 3.3 70B).

## 🔪 View the Demo  
**Travel Plan Creator:**
👉 https://contentcreator-travelplan.streamlit.app/

**Packing List Page:**
👉 https://travel-list-jonas.netlify.app/

---

## ✨ Features

- 🧠 **Interactive Chat AI**: Guides users through travel planning using `<CHAT>` and `<CONTENT>` structured prompts.
- 📍 **Dynamic Travel Map**: Displays route and travel stops using Google Maps JavaScript API.
- 👛 **Personalized Guidebook**: Updates structured travel profile with name, destination, style, budget, etc.
- 🌆 **Location Extraction**: Parses travel content into day-wise locations for route visualization.
- 🔐 **Secure API Key Handling**: Uses `.env` and `secrets.toml` to manage Groq and Google Maps API keys securely.
- 🚀 **FastAPI Backend**: Hosts `/travel_plan_api` endpoint for content generation with Groq’s LLMs.

---

## ⚙️ Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install required packages

```bash
pip install -r requirements.txt
```

### 3. Set up API keys

- Complete `.env.example` and rename to `.env`
- Complete `.streamlit/secrets.toml.example` and rename to `.streamlit/secrets.toml`
- Make sure **Google Maps API Key** allows unrestricted access or set proper referrer restrictions.

### 4. (For Ubuntu) Install Chromium and ChromeDriver

```bash
sudo apt-get install chromium-browser chromium-chromedriver
```

---

## ▶️ Running the App

### Run FastAPI backend locally

```bash
uvicorn main:app --reload
# or
python -m uvicorn main:app --reload
```

### Run Streamlit frontend

```bash
streamlit run streamlit_app.py
```

---

## 🙏 Credits

This project was built by Lydia as part of a team hackathon effort.  
Special thanks to [@prashantsingh2408](https://github.com/prashantsingh2408) for inspiration, code structure ideas, and collaborative planning support.

