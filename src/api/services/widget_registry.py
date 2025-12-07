"""Widget registry service for managing available widgets."""

from typing import Dict, List, Type, Optional
import logging
from dataclasses import dataclass

from ..widgets.base import BaseWidgetAdapter

logger = logging.getLogger(__name__)


@dataclass
class WidgetInfo:
    """Information about a registered widget."""
    name: str
    adapter_class: Type[BaseWidgetAdapter]
    description: str
    category: str
    requires_auth: bool = True
    timeout_seconds: int = 30


class WidgetRegistry:
    """Central registry for all available widget adapters."""
    
    def __init__(self):
        self._widgets: Dict[str, WidgetInfo] = {}
        self._categories: Dict[str, List[str]] = {}
        
    def register(self, 
                widget_name: str, 
                adapter_class: Type[BaseWidgetAdapter],
                description: str,
                category: str = "portfolio",
                requires_auth: bool = True,
                timeout_seconds: int = 30) -> None:
        """Register a widget adapter.
        
        Args:
            widget_name: Unique widget identifier
            adapter_class: Widget adapter class
            description: Human-readable description
            category: Widget category (portfolio, risk, performance, etc.)
            requires_auth: Whether widget requires authentication
            timeout_seconds: Maximum execution time
        """
        if widget_name in self._widgets:
            logger.warning(f"Widget '{widget_name}' already registered, overriding")
            
        widget_info = WidgetInfo(
            name=widget_name,
            adapter_class=adapter_class, 
            description=description,
            category=category,
            requires_auth=requires_auth,
            timeout_seconds=timeout_seconds
        )
        
        self._widgets[widget_name] = widget_info
        
        # Update category index
        if category not in self._categories:
            self._categories[category] = []
        if widget_name not in self._categories[category]:
            self._categories[category].append(widget_name)
            
        logger.info(f"Registered widget: {widget_name} ({category})")
        
    def get_widget(self, widget_name: str) -> Optional[WidgetInfo]:
        """Get widget information by name."""
        return self._widgets.get(widget_name)
        
    def get_adapter_class(self, widget_name: str) -> Optional[Type[BaseWidgetAdapter]]:
        """Get adapter class for a widget."""
        widget_info = self.get_widget(widget_name)
        return widget_info.adapter_class if widget_info else None
        
    def list_widgets(self, category: Optional[str] = None) -> List[WidgetInfo]:
        """List all registered widgets or widgets in a category."""
        if category:
            widget_names = self._categories.get(category, [])
            return [self._widgets[name] for name in widget_names]
        else:
            return list(self._widgets.values())
            
    def list_categories(self) -> List[str]:
        """List all widget categories."""
        return list(self._categories.keys())
        
    def is_registered(self, widget_name: str) -> bool:
        """Check if a widget is registered."""
        return widget_name in self._widgets
        
    def unregister(self, widget_name: str) -> bool:
        """Unregister a widget.
        
        Returns:
            True if widget was unregistered, False if not found
        """
        widget_info = self._widgets.pop(widget_name, None)
        if widget_info:
            # Remove from category index
            category_widgets = self._categories.get(widget_info.category, [])
            if widget_name in category_widgets:
                category_widgets.remove(widget_name)
            logger.info(f"Unregistered widget: {widget_name}")
            return True
        return False
        
    def get_widget_count(self) -> int:
        """Get total number of registered widgets."""
        return len(self._widgets)
        
    def get_category_count(self) -> int:
        """Get number of widget categories."""
        return len(self._categories)


# Global registry instance
widget_registry = WidgetRegistry()


def register_widget(widget_name: str, 
                   adapter_class: Type[BaseWidgetAdapter],
                   description: str,
                   category: str = "portfolio",
                   requires_auth: bool = True, 
                   timeout_seconds: int = 30) -> None:
    """Convenience function to register a widget with the global registry."""
    widget_registry.register(
        widget_name=widget_name,
        adapter_class=adapter_class,
        description=description,
        category=category,
        requires_auth=requires_auth,
        timeout_seconds=timeout_seconds
    )


def get_widget_adapter(widget_name: str, storage) -> Optional[BaseWidgetAdapter]:
    """Get an initialized widget adapter instance.
    
    Args:
        widget_name: Name of the widget
        storage: Database storage instance
        
    Returns:
        Initialized adapter instance or None if widget not found
    """
    adapter_class = widget_registry.get_adapter_class(widget_name)
    if adapter_class:
        # We'll need to determine the widget_class when implementing specific adapters
        return adapter_class(storage, None)  # placeholder
    return None