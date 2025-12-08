"""
ETF Analysis Dashboard - Home Page
"""

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

# Suppress pandas FutureWarnings
pd.set_option('future.no_silent_downcasting', True)

# Load environment variables
load_dotenv()

# DEPRECATION NOTICE - Phase out dates (configure via environment)
DEPRECATION_START = datetime.fromisoformat(
    os.getenv('DEPRECATION_START_DATE', '2024-12-08')
)
STREAMLIT_DISABLE_DATE = DEPRECATION_START + timedelta(weeks=8)
STREAMLIT_REMOVAL_DATE = STREAMLIT_DISABLE_DATE + timedelta(weeks=2)

days_until_disable = (STREAMLIT_DISABLE_DATE - datetime.now()).days
days_until_removal = (STREAMLIT_REMOVAL_DATE - datetime.now()).days

# Get dashboard URL from environment
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:3000/dashboard')

# Feature flags
STREAMLIT_ENABLED = os.getenv('STREAMLIT_ENABLED', 'true').lower() == 'true'
STREAMLIT_READ_ONLY = os.getenv('STREAMLIT_READ_ONLY', 'false').lower() == 'true'

# Check if Streamlit is disabled
if not STREAMLIT_ENABLED:
    st.error(f"""
    🚫 **Streamlit Interface Disabled**
    
    The Streamlit interface has been disabled. Please use the new Next.js dashboard:
    
    🌐 {DASHBOARD_URL}
    """)
    st.stop()

# Page configuration
st.set_page_config(
    page_title="ETF Analysis Dashboard - Home (DEPRECATED)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Show deprecation warning
st.warning(f"""
⚠️ **DEPRECATION NOTICE** ⚠️

The Streamlit interface is being **phased out and will be removed**.

🌐 **New Dashboard**: [{DASHBOARD_URL}]({DASHBOARD_URL})

✨ **Why Switch?**
- Modern, responsive design
- Drag-and-drop widget management
- Faster performance
- Better mobile support
- Same features, better experience

📅 **Important Dates**:
- ✅ **Now - {STREAMLIT_DISABLE_DATE.strftime('%b %d, %Y')}**: Both interfaces available ({days_until_disable} days)
- ⚠️ **{STREAMLIT_DISABLE_DATE.strftime('%b %d, %Y')}**: Streamlit becomes **read-only**
- 🗓️ **{STREAMLIT_REMOVAL_DATE.strftime('%b %d, %Y')}**: Streamlit **fully removed** ({days_until_removal} days)

📖 **Need Help?** [Migration Guide](https://github.com/doylet/etf-analysis/blob/main/docs/MIGRATION-GUIDE.md)

⚠️ **Action Required**: Please switch to the new dashboard before {STREAMLIT_DISABLE_DATE.strftime('%b %d, %Y')}.
""", icon="⚠️")

# Add countdown banner
if days_until_disable <= 14:
    st.error(f"""
    🚨 **URGENT**: Only **{days_until_disable} days** until Streamlit becomes read-only!
    Switch to the new dashboard NOW: [{DASHBOARD_URL}]({DASHBOARD_URL})
    """, icon="🚨")

# Show read-only mode warning
if STREAMLIT_READ_ONLY:
    st.warning(f"""
    📖 **Read-Only Mode**
    
    The Streamlit interface is now in read-only mode. You can view data but cannot make changes.
    
    To manage your portfolio, use the new dashboard:
    🌐 {DASHBOARD_URL}
    """)

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Add deprecation to sidebar
with st.sidebar:
    st.error("⚠️ This interface is deprecated")
    st.markdown(f"**{days_until_disable} days** until read-only")
    if st.button("Switch to New Dashboard", use_container_width=True, type="primary"):
        st.markdown(f"[Open New Dashboard]({DASHBOARD_URL})")

pages = [
    st.Page("pages/Dashboard.py"),
    st.Page("pages/My_Orders.py"),
    st.Page("pages/Price_History.py"),
    st.Page("pages/Comparative_Analysis.py")
]

pg = st.navigation(pages)
pg.run()
