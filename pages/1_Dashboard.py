"""
Dashboard Page
"""

import streamlit as st
from src.services.storage_adapter import DataStorageAdapter
from src.controllers import DashboardPage

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_resource
def init_storage():
    return DataStorageAdapter()

storage = init_storage()
controller = DashboardPage(storage)
controller.render()
