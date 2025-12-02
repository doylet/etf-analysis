"""
Price History Page
"""

import streamlit as st
from src.services.storage_adapter import DataStorageAdapter
from src.controllers import PriceHistoryPage

st.set_page_config(
    page_title="Price History",
    layout="wide"
)

@st.cache_resource
def init_storage():
    return DataStorageAdapter()

storage = init_storage()
controller = PriceHistoryPage(storage)
controller.render()
