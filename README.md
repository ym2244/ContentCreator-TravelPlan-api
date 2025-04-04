# Content Creator Chat Travel Plan API

# View demo at https://contentcreator-travelplan.streamlit.app/ 

# Setup
## Create a virtual environment
    python -m venv venv
## Activate the virtual environment
## Windows
    venv\Scripts\activate
## macOS/Linux
    source venv/bin/activate

## Install required packages
    pip install -r requirements.txt

## Set API Key
    Complete .env.example and .streamlit\secrets.toml.example
    (set Application Restrictions to None for Google API Key)

## Install Chromium and ChromeDriver (for Ubuntu)
    sudo apt-get install    chromium-browser chromium-chromedriver

## Run the FastAPI application
    uvicorn main:app --reload
    OR
    python -m uvicorn main:app --reload

## (Optional) Run testing website simultaneous
    streamlit run streamlit_app.py
