"""
Manage Instruments Page
"""

import streamlit as st
from src.services import AlphaVantageClient
from src.services.storage_adapter import DataStorageAdapter
from src.controllers import ManageInstrumentsPage

st.set_page_config(
    page_title="Manage Instruments",
    page_icon="🔧",
    layout="wide"
)

@st.cache_resource
def init_services():
    storage = DataStorageAdapter()
    av_client = AlphaVantageClient()
    return storage, av_client

storage, av_client = init_services()
controller = ManageInstrumentsPage(storage, av_client)
controller.render()
