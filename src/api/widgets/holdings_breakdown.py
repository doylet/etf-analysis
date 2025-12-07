"""Holdings Breakdown Widget API Adapter."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import pandas as pd

from api.widgets.base import BaseWidgetAdapter
from api.widgets.exceptions import WidgetDataError, WidgetValidationError
from api.schemas.widgets import HoldingsBreakdownData, CategoryBreakdown
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
        """Extract holdings breakdown calculation data from widget.
        
        This method properly delegates to the existing widget's calculation logic
        without duplicating any business logic (proper adapter pattern).
        """
        try:
            # Get instruments data from storage (same as widget does)
            instruments = self.storage.get_all_instruments()
            
            if not instruments:
                logger.warning("No instruments found for holdings breakdown")
                raise WidgetDataError(
                    "No instruments found in portfolio. Please add some positions first.",
                    error_code="NO_INSTRUMENTS"
                )
                
            # Get holdings with quantities > 0 (same logic as widget)
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
            
            # **DELEGATE TO EXISTING WIDGET** - Use existing calculation logic!
            try:
                # Use the widget's data fetching method to get processed holdings
                holdings_data = widget_instance._fetch_holdings_data(holdings)
                
                if holdings_data is None or holdings_data.df.empty:
                    raise WidgetDataError(
                        "No valid holdings data available",
                        error_code="NO_HOLDINGS_DATA"
                    )
                
                # Use the widget's calculation methods for breakdowns
                breakdown_data = self._convert_widget_data_to_api_format(
                    holdings_data, widget_instance, holdings
                )
                
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
    
    def _convert_widget_data_to_api_format(self, holdings_data, widget_instance, original_holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert the existing widget's data format to API response format.
        
        This is pure data transformation, not business logic duplication.
        """
        df = holdings_data.df
        total_value = holdings_data.total_value
        
        # Convert holdings DataFrame to API format
        individual_holdings = []
        for _, row in df.iterrows():
            holding = {
                "symbol": str(row.get('Symbol', '')),
                "name": str(row.get('Name', '')),
                "quantity": float(row.get('Quantity', 0)),
                "current_price": float(row.get('Price', 0)),
                "market_value": float(row.get('Value', 0)),
                "sector": str(row.get('Sector', 'Unknown')) if row.get('Sector') is not None else 'Unknown',
                "geography": str(row.get('Geography', row.get('Currency', 'Unknown')) if row.get('Geography') is not None else row.get('Currency', 'Unknown')),
                "asset_class": str(row.get('Type', 'Equity')) if row.get('Type') is not None else 'Equity',
                "weight": float(row.get('Value', 0) / total_value if total_value > 0 else 0.0)
            }
            individual_holdings.append(holding)
        
        # Use the widget's existing calculation methods for breakdowns
        sector_breakdown_df = widget_instance._calculate_grouped_breakdown(df, 'Sector', total_value)
        sector_breakdown = self._convert_breakdown_df_to_api(sector_breakdown_df)
        
        # For asset class (Type in the widget)
        asset_class_breakdown_df = widget_instance._calculate_grouped_breakdown(df, 'Type', total_value)
        asset_class_breakdown = self._convert_breakdown_df_to_api(asset_class_breakdown_df, key_column='Type')
        
        # Geography breakdown (use Currency as proxy for now)
        geography_breakdown = []
        if 'Currency' in df.columns:
            geography_breakdown_df = widget_instance._calculate_grouped_breakdown(df, 'Currency', total_value)
            geography_breakdown = self._convert_breakdown_df_to_api(geography_breakdown_df, key_column='Currency')
        
        # Calculate concentration risk using existing data
        concentration_score = self._calculate_concentration_risk_from_weights([h['weight'] for h in individual_holdings])
        
        return {
            "holdings": individual_holdings,
            "total_positions": len(individual_holdings),
            "total_value": total_value,
            "breakdown_by_sector": sector_breakdown,
            "breakdown_by_geography": geography_breakdown,
            "breakdown_by_asset_class": asset_class_breakdown,
            "concentration_risk_score": concentration_score,
            "last_updated": datetime.utcnow()
        }
    
    def _convert_breakdown_df_to_api(self, breakdown_df: pd.DataFrame, key_column: str = 'Sector') -> List[Dict[str, Any]]:
        """Convert widget breakdown DataFrame to API format."""
        breakdown = []
        for _, row in breakdown_df.iterrows():
            breakdown.append({
                'name': row[key_column],
                'value': row['Value'],
                'weight': row['Allocation %'] / 100.0,  # Convert percentage to decimal
                'positions': 1  # Could be enhanced to count positions per category
            })
        return breakdown
    
    def _calculate_concentration_risk_from_weights(self, weights: List[float]) -> float:
        """Calculate concentration risk score from position weights (simplified HHI)."""
        if not weights:
            return 0.0
            
        # Calculate Herfindahl-Hirschman Index (HHI)
        weights_squared = [w ** 2 for w in weights]
        hhi = sum(weights_squared)
        
        # Normalize to 0-1 scale (1 = maximum concentration, 0 = perfectly diversified)
        n_positions = len(weights)
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