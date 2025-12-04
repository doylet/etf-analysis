"""
Compatibility Layer

Provides backward compatibility bridges between legacy widget code 
and new service layer.
"""

from .streamlit_bridge import StreamlitServiceBridge

__all__ = ['StreamlitServiceBridge']
