"""
Price History Page
"""

import streamlit as st
import os
from src.services.storage_adapter import DataStorageAdapter
from src.controllers import PriceHistoryPage

st.set_page_config(
    page_title="Price History (DEPRECATED)",
    layout="wide"
)

# Deprecation warning
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:3000/dashboard')
st.warning(f"⚠️ This page is deprecated. Use the new dashboard price charts: [{DASHBOARD_URL}]({DASHBOARD_URL})", icon="⚠️")

@st.cache_resource
def init_storage():
    return DataStorageAdapter()

storage = init_storage()
controller = PriceHistoryPage(storage)
controller.render()
