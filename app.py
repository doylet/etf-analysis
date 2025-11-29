"""
ETF Analysis Dashboard - Main Application Entry Point
"""

import streamlit as st
from src.services import AlphaVantageClient
from src.services.storage_adapter import DataStorageAdapter
from src.controllers import (
    ManageInstrumentsPage,
    DashboardPage,
    PriceHistoryPage,
    ComparativeAnalysisPage
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ETF Analysis Dashboard",
    page_icon="📊",
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


# Initialize services
@st.cache_resource
def init_services():
    storage = DataStorageAdapter()
    av_client = AlphaVantageClient()
    return storage, av_client


def main():
    """Main application entry point"""
    storage, av_client = init_services()
    
    # Sidebar navigation
    st.sidebar.title("Analysis Dashboard")
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Manage Instruments", "Price History", "Comparative Analysis"]
    )
    
    # Route to appropriate page controller
    if page == "Manage Instruments":
        controller = ManageInstrumentsPage(storage, av_client)
    elif page == "Dashboard":
        controller = DashboardPage(storage)
    elif page == "Price History":
        controller = PriceHistoryPage(storage)
    elif page == "Comparative Analysis":
        controller = ComparativeAnalysisPage(storage)
    
    # Render the page
    controller.render()
    
    # Footer
    st.sidebar.divider()
    st.sidebar.caption("Analysis Dashboard")
    # st.sidebar.caption("Built with Streamlit")


if __name__ == "__main__":
    main()
