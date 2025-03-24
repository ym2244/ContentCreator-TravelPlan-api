## 🌍 Google Maps API Key Setup

This project uses **Google Maps Geocoding API** and **Maps JavaScript API** to display travel routes. Follow these steps to enable the features:

---

### ✅ 1. Create an API Key

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Generate API key

---

### ✅ 2. Enable Required APIs

In [API Library](https://console.cloud.google.com/apis/library), enable:

- `Geocoding API`
- `Maps JavaScript API`

---

### ✅ 3. Configure API Key Restrictions

Go back to [Credentials (https://console.cloud.google.com/apis/credentials), click on your created key to open its settings::

- **Application Restrictions**: set to **None** (recommended for local testing)
- **API Restrictions**: restrict to:
  - `Geocoding API`
  - `Maps JavaScript API`

Save and wait 1–2 minutes for changes to apply.

---

### ✅ 4. Use Your API Key

#### Option 1: Streamlit (recommended)

Create `.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "your_api_key_here"
