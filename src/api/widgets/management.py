"""
Widget Management API

Provides REST endpoints for managing dashboard widgets:
- Get list of available widgets
- Get current active widgets
- Add/remove widgets from dashboard
- Reorder widgets
- Save/load widget configurations
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from storage.base import BaseStorage
import json


class WidgetOrder(BaseModel):
    """Model for widget ordering requests"""
    widget_ids: List[str]


class WidgetToggle(BaseModel):
    """Model for adding/removing widgets"""
    widget_id: str
    action: str  # 'add' or 'remove'


class WidgetManagementAPI:
    """API for managing dashboard widgets"""
    
    # Registry of available widgets matching dashboard controller
    AVAILABLE_WIDGETS = {
        'portfolio_summary': {
            'name': 'Portfolio Summary',
            'description': 'Overview of portfolio performance and key metrics',
            'category': 'overview'
        },
        'benchmark_comparison': {
            'name': 'Benchmark Comparison',
            'description': 'Compare portfolio performance against market benchmarks',
            'category': 'performance'
        },
        'portfolio_optimizer': {
            'name': 'Portfolio Optimizer',
            'description': 'Optimize portfolio allocation using modern portfolio theory',
            'category': 'optimization'
        },
        'constrained_optimization': {
            'name': 'Constrained Optimization',
            'description': 'Portfolio optimization with custom constraints',
            'category': 'optimization'
        },
        'monte_carlo': {
            'name': 'Monte Carlo Simulation',
            'description': 'Monte Carlo analysis of portfolio scenarios',
            'category': 'analysis'
        },
        'timeseries_analysis': {
            'name': 'Time Series Analysis',
            'description': 'Advanced time series analysis and forecasting',
            'category': 'analysis'
        },
        'holdings_breakdown': {
            'name': 'Holdings Breakdown',
            'description': 'Detailed breakdown of portfolio holdings',
            'category': 'overview'
        },
        'portfolio_transition': {
            'name': 'Portfolio Transition',
            'description': 'Analyze portfolio rebalancing and transition costs',
            'category': 'management'
        },
        'news_event_analysis': {
            'name': 'News & Event Analysis',
            'description': 'Impact of news and events on portfolio performance',
            'category': 'analysis'
        },
        'performance': {
            'name': 'Performance Analysis',
            'description': 'Comprehensive performance metrics and analysis',
            'category': 'performance'
        },
        'dividend_analysis': {
            'name': 'Dividend Analysis',
            'description': 'Analyze dividend payments and income projections',
            'category': 'income'
        },
        'correlation_matrix': {
            'name': 'Correlation Matrix',
            'description': 'Correlation analysis between portfolio assets',
            'category': 'analysis'
        }
    }
    
    def __init__(self, storage: BaseStorage):
        self.storage = storage
    
    def get_available_widgets(self) -> Dict[str, Any]:
        """Get list of all available widgets"""
        try:
            return {
                'success': True,
                'widgets': self.AVAILABLE_WIDGETS,
                'categories': {
                    'overview': 'Portfolio Overview',
                    'performance': 'Performance Analysis',
                    'analysis': 'Advanced Analysis',
                    'optimization': 'Portfolio Optimization',
                    'management': 'Portfolio Management',
                    'income': 'Income Analysis'
                },
                'metadata': {
                    'total_widgets': len(self.AVAILABLE_WIDGETS),
                    'timestamp': self.storage.get_current_timestamp()
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get available widgets: {str(e)}")
    
    def get_active_widgets(self) -> Dict[str, Any]:
        """Get list of currently active widgets"""
        try:
            # Load widget configuration from database
            saved_widgets = self.storage.get_setting('dashboard_widgets')
            
            if saved_widgets:
                try:
                    active_widget_ids = json.loads(saved_widgets)
                except json.JSONDecodeError:
                    # Fallback to defaults if JSON parsing fails
                    active_widget_ids = ['portfolio_summary', 'benchmark_comparison', 'holdings_breakdown']
            else:
                # Default widgets on first load
                active_widget_ids = ['portfolio_summary', 'benchmark_comparison', 'holdings_breakdown']
            
            # Get details for active widgets
            active_widgets = []
            for widget_id in active_widget_ids:
                if widget_id in self.AVAILABLE_WIDGETS:
                    widget_info = self.AVAILABLE_WIDGETS[widget_id].copy()
                    widget_info['id'] = widget_id
                    widget_info['order'] = len(active_widgets)
                    active_widgets.append(widget_info)
            
            return {
                'success': True,
                'active_widgets': active_widgets,
                'widget_ids': active_widget_ids,
                'metadata': {
                    'active_count': len(active_widgets),
                    'timestamp': self.storage.get_current_timestamp()
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get active widgets: {str(e)}")
    
    def toggle_widget(self, widget_toggle: WidgetToggle) -> Dict[str, Any]:
        """Add or remove a widget from the active dashboard"""
        try:
            # Validate widget exists
            if widget_toggle.widget_id not in self.AVAILABLE_WIDGETS:
                raise HTTPException(status_code=400, detail=f"Widget '{widget_toggle.widget_id}' not found")
            
            # Load current active widgets
            current_widgets = self.get_active_widgets()['widget_ids']
            
            if widget_toggle.action == 'add':
                if widget_toggle.widget_id not in current_widgets:
                    current_widgets.append(widget_toggle.widget_id)
                    action_performed = 'added'
                else:
                    action_performed = 'already_active'
            
            elif widget_toggle.action == 'remove':
                if widget_toggle.widget_id in current_widgets:
                    current_widgets.remove(widget_toggle.widget_id)
                    action_performed = 'removed'
                else:
                    action_performed = 'not_active'
            
            else:
                raise HTTPException(status_code=400, detail="Action must be 'add' or 'remove'")
            
            # Save updated widget configuration
            self._save_widget_configuration(current_widgets)
            
            return {
                'success': True,
                'action_performed': action_performed,
                'widget_id': widget_toggle.widget_id,
                'widget_name': self.AVAILABLE_WIDGETS[widget_toggle.widget_id]['name'],
                'active_widgets': current_widgets,
                'metadata': {
                    'active_count': len(current_widgets),
                    'timestamp': self.storage.get_current_timestamp()
                }
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Failed to toggle widget: {str(e)}")
    
    def reorder_widgets(self, widget_order: WidgetOrder) -> Dict[str, Any]:
        """Reorder active widgets"""
        try:
            # Validate all widgets exist and are valid
            for widget_id in widget_order.widget_ids:
                if widget_id not in self.AVAILABLE_WIDGETS:
                    raise HTTPException(status_code=400, detail=f"Widget '{widget_id}' not found")
            
            # Save new widget order
            self._save_widget_configuration(widget_order.widget_ids)
            
            # Get updated active widgets with new order
            updated_widgets = self.get_active_widgets()
            
            return {
                'success': True,
                'message': 'Widget order updated successfully',
                'active_widgets': updated_widgets['active_widgets'],
                'widget_ids': widget_order.widget_ids,
                'metadata': {
                    'reordered_count': len(widget_order.widget_ids),
                    'timestamp': self.storage.get_current_timestamp()
                }
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Failed to reorder widgets: {str(e)}")
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        """Reset widget configuration to defaults"""
        try:
            default_widgets = ['portfolio_summary', 'benchmark_comparison', 'holdings_breakdown']
            self._save_widget_configuration(default_widgets)
            
            return {
                'success': True,
                'message': 'Widget configuration reset to defaults',
                'active_widgets': default_widgets,
                'metadata': {
                    'reset_timestamp': self.storage.get_current_timestamp()
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to reset widgets: {str(e)}")
    
    def _save_widget_configuration(self, widget_ids: List[str]):
        """Save widget configuration to database"""
        try:
            widgets_json = json.dumps(widget_ids)
            self.storage.set_setting(
                'dashboard_widgets',
                widgets_json,
                'Active dashboard widgets configuration'
            )
        except Exception as e:
            raise Exception(f"Failed to save widget configuration: {str(e)}")


def create_widget_management_router(storage: BaseStorage) -> APIRouter:
    """Create FastAPI router for widget management endpoints"""
    router = APIRouter(prefix="/api/widgets", tags=["Widget Management"])
    widget_api = WidgetManagementAPI(storage)
    
    @router.get("/available")
    async def get_available_widgets():
        """Get list of all available widgets"""
        return widget_api.get_available_widgets()
    
    @router.get("/active")
    async def get_active_widgets():
        """Get list of currently active widgets"""
        return widget_api.get_active_widgets()
    
    @router.post("/toggle")
    async def toggle_widget(widget_toggle: WidgetToggle):
        """Add or remove a widget from the dashboard"""
        return widget_api.toggle_widget(widget_toggle)
    
    @router.post("/reorder")
    async def reorder_widgets(widget_order: WidgetOrder):
        """Reorder active widgets"""
        return widget_api.reorder_widgets(widget_order)
    
    @router.post("/reset")
    async def reset_widgets():
        """Reset widget configuration to defaults"""
        return widget_api.reset_to_defaults()
    
    return router