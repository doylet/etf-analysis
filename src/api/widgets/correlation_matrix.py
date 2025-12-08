"""Correlation Matrix Widget API Adapter."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import pandas as pd

from src.api.widgets.base import BaseWidgetAdapter
from src.api.widgets.exceptions import WidgetDataError, WidgetValidationError
from api.schemas.widgets import CorrelationMatrixData
from api.services.widget_cache import widget_cache
from api.services.performance_monitor import monitor_widget_performance
from widgets.correlation_matrix_widget import CorrelationMatrixWidget

logger = logging.getLogger(__name__)


class CorrelationMatrixAdapter(BaseWidgetAdapter):
    """Adapter to expose correlation matrix widget through API."""
    
    # Correlation matrix cache TTL (15 minutes - complex calculation, less frequent updates)
    CACHE_TTL_MINUTES = 15
    
    def __init__(self, storage):
        super().__init__(storage, CorrelationMatrixWidget)
        
    def get_widget_name(self) -> str:
        return "correlation_matrix"
        
    def get_widget_description(self) -> str:
        return "Asset correlation analysis between portfolio holdings and benchmarks"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate parameters for correlation matrix analysis."""
        validated = {}
        
        # Portfolio ID is optional
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
            
        # Time window for correlation analysis
        time_window_days = kwargs.get('time_window_days', 252)  # Default 1 year
        if not isinstance(time_window_days, (int, float)) or time_window_days <= 0:
            raise WidgetValidationError("time_window_days must be a positive number")
        validated['time_window_days'] = int(time_window_days)
        
        # Additional benchmarks to include
        additional_symbols = kwargs.get('additional_symbols', ['SPY', 'QQQ'])
        if not isinstance(additional_symbols, list):
            raise WidgetValidationError("additional_symbols must be a list")
        validated['additional_symbols'] = [str(s).upper().strip() for s in additional_symbols]
        
        # Include portfolio holdings in analysis
        include_holdings = kwargs.get('include_holdings', True)
        validated['include_holdings'] = bool(include_holdings)
            
        return validated
        
    def extract_calculation_data(self, widget_instance) -> Dict[str, Any]:
        """Extract correlation matrix calculation data from widget.
        
        This method properly delegates to the existing widget's calculation logic
        without duplicating any business logic (proper adapter pattern).
        """
        try:
            # Get instruments data from storage (same as widget does)
            instruments = self.storage.get_all_instruments()
            
            if not instruments:
                logger.warning("No instruments found for correlation analysis")
                raise WidgetDataError(
                    "No instruments found in portfolio. Please add some positions first.",
                    error_code="NO_INSTRUMENTS"
                )
                
            # Get holdings with quantities > 0 (same logic as widget)
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            
            if not holdings:
                logger.info("Portfolio exists but all positions have zero quantity")
                return self._empty_correlation_response()
            
            # **DELEGATE TO EXISTING WIDGET** - Use existing calculation logic!
            try:
                correlation_analysis = self._calculate_correlation_using_widget(
                    widget_instance, holdings, self.validated_params
                )
                
                if correlation_analysis is None:
                    raise WidgetDataError(
                        "Correlation analysis returned no results",
                        error_code="NO_CORRELATION_DATA"
                    )
                
                # Convert existing widget data to API format
                api_response = self._convert_correlation_data_to_api_format(correlation_analysis)
                
            except Exception as calc_error:
                logger.error(f"Correlation matrix calculation failed: {calc_error}")
                raise WidgetDataError(
                    f"Correlation matrix calculation failed: {str(calc_error)}",
                    error_code="CALCULATION_ERROR"
                )
            
            return api_response
            
        except WidgetDataError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting correlation matrix: {e}", exc_info=True)
            raise WidgetDataError(
                f"Failed to extract correlation matrix: {str(e)}",
                error_code="UNEXPECTED_ERROR"
            )
    
    def _calculate_correlation_using_widget(self, widget_instance, holdings: List[Dict[str, Any]], params: Dict[str, Any]):
        """Use the existing widget's calculation methods."""
        # Set up parameters for widget calculation
        time_window = params.get('time_window_days', 252)
        additional_symbols = params.get('additional_symbols', ['SPY', 'QQQ'])
        include_holdings = params.get('include_holdings', True)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=time_window + 50)  # Add buffer for missing data
        
        # Get portfolio symbols for analysis
        selected_holdings = []
        if include_holdings:
            selected_holdings = [h.get('symbol', '') for h in holdings if h.get('symbol')]
        
        # Combine all symbols for analysis
        all_symbols = selected_holdings + additional_symbols
        
        if len(all_symbols) < 2:
            logger.warning("Need at least 2 symbols for correlation analysis")
            return None
        
        # Use the widget's data fetching method
        try:
            returns_result = widget_instance._fetch_returns_data(
                all_symbols, selected_holdings, start_date, end_date, 
                False, holdings  # include_portfolio=False for API simplicity
            )
            
            if returns_result.get('status') == 'error':
                logger.error(f"Data fetch failed: {returns_result.get('message')}")
                return None
                
            returns_df = returns_result.get('returns_df')
            if returns_df is None or returns_df.empty:
                logger.warning("No returns data available for correlation analysis")
                return None
                
            # Use widget's correlation analysis method (static method)
            correlation_analysis = CorrelationMatrixWidget._calculate_correlation_analysis(
                returns_df,
                selected_holdings,
                additional_symbols,
                start_date,
                end_date
            )
            
            return correlation_analysis
            
        except Exception as e:
            logger.error(f"Widget correlation calculation failed: {e}")
            raise
    
    def _convert_correlation_data_to_api_format(self, correlation_analysis) -> Dict[str, Any]:
        """Convert the existing widget's correlation analysis to API response format."""
        # Convert correlation matrix to serializable format
        correlation_matrix = correlation_analysis.correlation_matrix
        matrix_data = []
        symbols = list(correlation_matrix.index)
        
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols):
                matrix_data.append({
                    "symbol1": symbol1,
                    "symbol2": symbol2,
                    "correlation": float(correlation_matrix.iloc[i, j])
                })
        
        # Convert correlation pairs to API format
        pairs_data = []
        if correlation_analysis.pairs_df is not None and not correlation_analysis.pairs_df.empty:
            for _, row in correlation_analysis.pairs_df.iterrows():
                # Parse the pair format "SYMBOL1 - SYMBOL2"
                pair_str = str(row.get('Pair', ''))
                if ' - ' in pair_str:
                    asset1, asset2 = pair_str.split(' - ', 1)
                    pairs_data.append({
                        "asset1": asset1.strip(),
                        "asset2": asset2.strip(),
                        "correlation": float(row.get('Correlation', 0.0))
                    })
                else:
                    # Fallback if format is different
                    pairs_data.append({
                        "asset1": pair_str,
                        "asset2": "",
                        "correlation": float(row.get('Correlation', 0.0))
                    })
        
        # Convert benchmark comparison if available
        benchmark_comparison = []
        if correlation_analysis.benchmark_pivot is not None:
            for _, row in correlation_analysis.benchmark_pivot.iterrows():
                benchmark_data = {"benchmark": str(row.name)}
                for col in correlation_analysis.benchmark_pivot.columns:
                    benchmark_data[str(col)] = float(row[col]) if pd.notna(row[col]) else None
                benchmark_comparison.append(benchmark_data)
        
        return {
            "symbols": symbols,
            "correlation_matrix": matrix_data,
            "correlation_pairs": pairs_data,
            "benchmark_comparison": benchmark_comparison,
            "statistics": {
                "avg_correlation": float(correlation_analysis.avg_correlation),
                "max_correlation": float(correlation_analysis.max_correlation),
                "min_correlation": float(correlation_analysis.min_correlation),
                "num_days": int(correlation_analysis.num_days)
            },
            "analysis_period": {
                "start_date": correlation_analysis.start_date.isoformat(),
                "end_date": correlation_analysis.end_date.isoformat(),
                "days_analyzed": int(correlation_analysis.num_days)
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _empty_correlation_response(self) -> Dict[str, Any]:
        """Return empty correlation response structure."""
        return {
            "symbols": [],
            "correlation_matrix": [],
            "correlation_pairs": [],
            "benchmark_comparison": [],
            "statistics": {
                "avg_correlation": 0.0,
                "max_correlation": 0.0,
                "min_correlation": 0.0,
                "num_days": 0
            },
            "analysis_period": {
                "start_date": datetime.utcnow().isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "days_analyzed": 0
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute correlation matrix analysis with caching and performance monitoring."""
        # Validate parameters
        self.validated_params = self.validate_input_parameters(**kwargs)
        
        # Check cache first
        cached_result = widget_cache.get(self.get_widget_name(), self.validated_params)
        
        if cached_result:
            logger.debug(f"Cache hit for correlation matrix")
            # Add cache metadata
            cached_result["metadata"] = cached_result.get("metadata", {})
            cached_result["metadata"]["cache_hit"] = True
            cached_result["metadata"]["cached_at"] = cached_result.get("cached_at")
            return cached_result
        
        # Execute calculation with performance monitoring
        with monitor_widget_performance(self.get_widget_name(), self.validated_params):
            try:
                # Create widget instance and execute calculation
                widget_instance = self._create_widget_instance(self.validated_params)
                calculation_data = self.extract_calculation_data(widget_instance)
                
                # Prepare response
                result = {
                    "widget_name": self.get_widget_name(),
                    "success": True,
                    "data": calculation_data,
                    "metadata": {
                        "execution_time": datetime.now().isoformat(),
                        "parameters": self.validated_params,
                        "widget_description": self.get_widget_description(),
                        "cache_hit": False
                    },
                    "error": None
                }
                
                # Cache the successful result
                widget_cache.set(
                    self.get_widget_name(), 
                    self.validated_params, 
                    result,
                    ttl_minutes=self.CACHE_TTL_MINUTES
                )
                
                logger.debug(f"Correlation matrix calculated and cached")
                return result
                
            except Exception as e:
                logger.error(f"Correlation matrix calculation failed: {e}")
                # Don't cache errors, return them directly
                return {
                    "widget_name": self.get_widget_name(),
                    "success": False,
                    "data": None,
                    "metadata": {
                        "execution_time": datetime.now().isoformat(),
                        "parameters": self.validated_params,
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
        """Create correlation matrix widget instance."""
        widget_id = f"correlation_matrix_{hash(str(validated_params))}"
        widget = self.widget_class(self.storage, widget_id)
        
        # Set portfolio ID if provided
        if validated_params.get('portfolio_id'):
            widget.portfolio_id = validated_params['portfolio_id']
            
        return widget