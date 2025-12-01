"""
My Orders page controller
"""

import streamlit as st
from ..base import BaseController
from .list_component import InstrumentListComponent
from .data_controls_component import DataControlsComponent
from .order_component import OrderFormComponent
from .order_history_component import OrderHistoryComponent


class MyOrdersPage(BaseController):
    """Controller for My Orders page - orchestrates components"""
    
    def render(self):
        st.title("My Orders")
        st.write("Record trades and manage your portfolio holdings.")
        
        # Always reload instruments fresh from database
        instruments = self._load_instruments(active_only=True)
        
        # Debug info
        st.caption(f"Found {len(instruments)} active instruments")
        
        if instruments:
            # Render portfolio holdings list first
            list_component = InstrumentListComponent(self.storage, instruments)
            list_component.render()
            
            # Render data controls
            data_controls = DataControlsComponent(self.storage, instruments)
            data_controls.render()
            
            
            
            # Render order form
            order_form = OrderFormComponent(self.storage, self.av_client, instruments)
            order_form.render()
            
            
            
            # Render order history
            order_history = OrderHistoryComponent(self.storage)
            order_history.render()
        else:
            st.info("No instruments or orders yet. Record your first trade below!")
            
            # Show order form even with no instruments
            order_form = OrderFormComponent(self.storage, self.av_client, instruments)
            order_form.render()
