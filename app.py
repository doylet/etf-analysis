"""
ETF Analysis Dashboard - Home Page
"""

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ETF Analysis Dashboard - Home",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

st.title("ETF Analysis Dashboard")

st.markdown("""
## Welcome to the ETF Analysis Dashboard

Use the sidebar navigation to explore different sections:

### Dashboard
View portfolio overview and manage data for all tracked instruments.

### Manage Instruments
Add, remove, and update instruments. Search for symbols using Alpha Vantage integration.

### Price History
Analyze historical price data and trading volumes for individual instruments.

### Comparative Analysis
Compare performance across multiple instruments with normalized charts.

---

**Get started by selecting a page from the sidebar!**
""")

st.sidebar.success("Select a page above.")
