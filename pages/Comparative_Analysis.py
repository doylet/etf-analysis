"""
Comparative Analysis Page
"""

import streamlit as st
from src.services.storage_adapter import DataStorageAdapter
from src.controllers import ComparativeAnalysisPage

st.set_page_config(
    page_title="Comparative Analysis",
    layout="wide"
)

@st.cache_resource
def init_storage():
    return DataStorageAdapter()

storage = init_storage()
controller = ComparativeAnalysisPage(storage)
controller.render()
