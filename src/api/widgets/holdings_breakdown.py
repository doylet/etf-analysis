"""Holdings Breakdown Widget API Adapter."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from api.widgets.base import BaseWidgetAdapter
from api.widgets.exceptions import WidgetDataError, WidgetValidationError
from api.schemas.widgets import HoldingsBreakdownData
from api.services.widget_cache import widget_cache
from api.services.performance_monitor import monitor_widget_performance
from widgets.holdings_breakdown_widget import HoldingsBreakdownWidget

logger = logging.getLogger(__name__)


class HoldingsBreakdownAdapter(BaseWidgetAdapter):
    """Adapter to expose holdings breakdown widget through API."""
    
    # Holdings breakdown cache TTL (10 minutes - less frequent updates)
    CACHE_TTL_MINUTES = 10
    
    def __init__(self, storage):
        super().__init__(storage, HoldingsBreakdownWidget)
        
    def get_widget_name(self) -> str:
        return "holdings_breakdown"
        
    def get_widget_description(self) -> str:
        return "Portfolio holdings breakdown by sector, geography, and asset class"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate parameters for holdings breakdown."""
        validated = {}
        
        # Portfolio ID is optional
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
            
        # Breakdown type parameter
        breakdown_type = kwargs.get('breakdown_type', 'sector')
        valid_types = ['sector', 'geography', 'asset_class', 'all']
        if breakdown_type not in valid_types:
            raise WidgetValidationError(
                f"breakdown_type must be one of {valid_types}, got: {breakdown_type}"
            )
        validated['breakdown_type'] = breakdown_type
        
        # Include percentages option
        include_percentages = kwargs.get('include_percentages', True)
        validated['include_percentages'] = bool(include_percentages)
            
        return validated
        
    def extract_calculation_data(self, widget_instance) -> Dict[str, Any]:
        """Extract holdings breakdown calculation data from widget."""
        try:
            # Get instruments data from storage
            instruments = self.storage.get_all_instruments()
            
            if not instruments:
                logger.warning("No instruments found for holdings breakdown")
                raise WidgetDataError(
                    "No instruments found in portfolio. Please add some positions first.",
                    error_code="NO_INSTRUMENTS"
                )
                
            # Get holdings with quantities > 0
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            
            if not holdings:
                logger.info("Portfolio exists but all positions have zero quantity")
                return {
                    "holdings": [],
                    "total_positions": 0,
                    "total_value": 0.0,
                    "breakdown_by_sector": [],
                    "breakdown_by_geography": [],
                    "breakdown_by_asset_class": [],
                    "concentration_risk_score": 0.0,
                    "last_updated": datetime.utcnow()
                }
            
            # Verify we have price data for holdings
            holdings_with_prices = [h for h in holdings if h.get('current_price') is not None]
            if not holdings_with_prices:
                logger.error("Holdings found but no current price data available")
                raise WidgetDataError(
                    "Holdings found but no current price data available. Please check data connections.",
                    error_code="NO_PRICE_DATA"
                )
            
            # Calculate holdings breakdown using widget logic
            try:
                breakdown_data = self._calculate_holdings_breakdown(holdings_with_prices, widget_instance)
            except Exception as calc_error:
                logger.error(f"Holdings breakdown calculation failed: {calc_error}")
                raise WidgetDataError(
                    f"Holdings breakdown calculation failed: {str(calc_error)}",
                    error_code="CALCULATION_ERROR"
                )
            
            return breakdown_data
            
        except WidgetDataError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting holdings breakdown: {e}", exc_info=True)
            raise WidgetDataError(
                f"Failed to extract holdings breakdown: {str(e)}",
                error_code="UNEXPECTED_ERROR"
            )
    
    def _calculate_holdings_breakdown(self, holdings: List[Dict[str, Any]], widget_instance) -> Dict[str, Any]:
        """Calculate holdings breakdown using widget calculation logic."""
        # Calculate individual position data
        positions = []
        total_value = 0.0
        
        for holding in holdings:
            symbol = holding.get('symbol', 'Unknown')
            quantity = holding.get('quantity', 0)
            current_price = holding.get('current_price', 0)
            market_value = quantity * current_price
            total_value += market_value
            
            positions.append({
                "symbol": symbol,
                "name": holding.get('name', symbol),
                "quantity": quantity,
                "current_price": current_price,
                "market_value": market_value,
                "sector": holding.get('sector', 'Unknown'),
                "geography": holding.get('geography', 'Unknown'),
                "asset_class": holding.get('asset_class', 'Equity'),
                "weight": 0.0  # Will be calculated below
            })
        
        # Calculate weights
        if total_value > 0:
            for position in positions:
                position["weight"] = position["market_value"] / total_value
        
        # Calculate breakdown by sector
        sector_breakdown = self._calculate_breakdown_by_category(positions, 'sector')
        
        # Calculate breakdown by geography
        geography_breakdown = self._calculate_breakdown_by_category(positions, 'geography')
        
        # Calculate breakdown by asset class
        asset_class_breakdown = self._calculate_breakdown_by_category(positions, 'asset_class')
        
        # Calculate concentration risk score (simplified)
        concentration_score = self._calculate_concentration_risk(positions)
        
        return {
            "holdings": positions,
            "total_positions": len(positions),
            "total_value": total_value,
            "breakdown_by_sector": sector_breakdown,
            "breakdown_by_geography": geography_breakdown,
            "breakdown_by_asset_class": asset_class_breakdown,
            "concentration_risk_score": concentration_score,
            "last_updated": datetime.utcnow()
        }
    
    def _calculate_breakdown_by_category(self, positions: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """Calculate breakdown by a specific category (sector, geography, asset_class)."""
        category_totals = {}
        total_value = sum(pos['market_value'] for pos in positions)
        
        # Aggregate by category
        for position in positions:
            cat_value = position.get(category, 'Unknown')
            if cat_value not in category_totals:
                category_totals[cat_value] = {
                    'name': cat_value,
                    'value': 0.0,
                    'weight': 0.0,
                    'positions': 0
                }
            
            category_totals[cat_value]['value'] += position['market_value']
            category_totals[cat_value]['positions'] += 1
        
        # Calculate percentages and sort
        breakdown = list(category_totals.values())
        for item in breakdown:
            item['weight'] = item['value'] / total_value if total_value > 0 else 0.0
        
        # Sort by value descending
        breakdown.sort(key=lambda x: x['value'], reverse=True)
        
        return breakdown
    
    def _calculate_concentration_risk(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate concentration risk score (0-1, higher = more concentrated)."""
        if not positions:
            return 0.0
            
        # Calculate Herfindahl-Hirschman Index (HHI)
        weights_squared = [pos['weight'] ** 2 for pos in positions]
        hhi = sum(weights_squared)
        
        # Normalize to 0-1 scale (1 = maximum concentration, 0 = perfectly diversified)
        # For N positions, minimum HHI is 1/N, maximum is 1
        n_positions = len(positions)
        min_hhi = 1.0 / n_positions if n_positions > 0 else 0
        max_hhi = 1.0
        
        if max_hhi > min_hhi:
            concentration_score = (hhi - min_hhi) / (max_hhi - min_hhi)
        else:
            concentration_score = 0.0
            
        return min(max(concentration_score, 0.0), 1.0)
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute holdings breakdown with caching and performance monitoring."""
        # Validate parameters
        validated_params = self.validate_input_parameters(**kwargs)
        
        # Check cache first
        cached_result = widget_cache.get(self.get_widget_name(), validated_params)
        
        if cached_result:
            logger.debug(f"Cache hit for holdings breakdown")
            # Add cache metadata
            cached_result["metadata"] = cached_result.get("metadata", {})
            cached_result["metadata"]["cache_hit"] = True
            cached_result["metadata"]["cached_at"] = cached_result.get("cached_at")
            return cached_result
        
        # Execute calculation with performance monitoring
        with monitor_widget_performance(self.get_widget_name(), validated_params):
            try:
                # Create widget instance and execute calculation
                widget_instance = self._create_widget_instance(validated_params)
                calculation_data = self.extract_calculation_data(widget_instance)
                
                # Prepare response
                result = {
                    "widget_name": self.get_widget_name(),
                    "success": True,
                    "data": calculation_data,
                    "metadata": {
                        "execution_time": datetime.now().isoformat(),
                        "parameters": validated_params,
                        "widget_description": self.get_widget_description(),
                        "cache_hit": False
                    },
                    "error": None
                }
                
                # Cache the successful result
                widget_cache.set(
                    self.get_widget_name(), 
                    validated_params, 
                    result,
                    ttl_minutes=self.CACHE_TTL_MINUTES
                )
                
                logger.debug(f"Holdings breakdown calculated and cached")
                return result
                
            except Exception as e:
                logger.error(f"Holdings breakdown calculation failed: {e}")
                # Don't cache errors, return them directly
                return {
                    "widget_name": self.get_widget_name(),
                    "success": False,
                    "data": None,
                    "metadata": {
                        "execution_time": datetime.now().isoformat(),
                        "parameters": validated_params,
                        "widget_description": self.get_widget_description(),
                        "cache_hit": False
                    },
                    "error": {
                        "code": getattr(e, 'code', 'CALCULATION_ERROR'),
                        "message": str(e),
                        "details": getattr(e, 'details', {})
                    }
                }
    
    def _create_widget_instance(self, validated_params: Dict[str, Any]):
        """Create holdings breakdown widget instance."""
        widget_id = f"holdings_breakdown_{hash(str(validated_params))}"
        widget = self.widget_class(self.storage, widget_id)
        
        # Set portfolio ID if provided
        if validated_params.get('portfolio_id'):
            widget.portfolio_id = validated_params['portfolio_id']
            
        return widget