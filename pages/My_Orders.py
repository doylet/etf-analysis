"""
My Orders Page
"""

import streamlit as st
import os
from src.services import AlphaVantageClient
from src.services.storage_adapter import DataStorageAdapter
from src.controllers import MyOrdersPage

st.set_page_config(
    page_title="My Orders (DEPRECATED)",
    layout="wide"
)

# Deprecation warning
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:3000/orders')
st.warning(f"⚠️ This page is deprecated. Use the new order management: [{DASHBOARD_URL}]({DASHBOARD_URL})", icon="⚠️")

@st.cache_resource
def init_services():
    storage = DataStorageAdapter()
    av_client = AlphaVantageClient()
    return storage, av_client

storage, av_client = init_services()
controller = MyOrdersPage(storage, av_client=av_client)
controller.render()
