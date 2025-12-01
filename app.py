"""
ETF Analysis Dashboard - Home Page
"""

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Page configuration
st.set_page_config(
    page_title="ETF Analysis Dashboard - Home",
    layout="wide",
    initial_sidebar_state="expanded"
)

pages = [
    st.Page("pages/Dashboard.py"),
    st.Page("pages/My_Orders.py"),
    st.Page("pages/Price_History.py"),
    st.Page("pages/Comparative_Analysis.py")
]

pg = st.navigation(pages)
pg.run()
