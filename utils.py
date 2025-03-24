def get_google_api_key():
    """
    Try to load GOOGLE_API_KEY from streamlit secrets first,
    then fall back to environment variable.
    """
    import os
    try:
        import streamlit as st
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except ImportError:
        pass  # Not using Streamlit, continue to env

    # Try from environment variable
    return os.environ.get("GOOGLE_API_KEY")
