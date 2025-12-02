"""
Base widget class for dashboard widgets
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import streamlit as st


class BaseWidget(ABC):
    """Base class for all dashboard widgets"""
    
    def __init__(self, storage, widget_id: str):
        self.storage = storage
        self.widget_id = widget_id
    
    @abstractmethod
    def get_name(self) -> str:
        """Return widget display name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return widget description"""
        pass
    
    @abstractmethod
    def get_scope(self) -> str:
        """Return widget scope: 'portfolio', 'single', or 'multiple'"""
        pass
    
    @abstractmethod
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Render the widget content"""
        pass
    
    def render_config(self) -> Dict:
        """Render widget configuration options (optional)"""
        return {}
