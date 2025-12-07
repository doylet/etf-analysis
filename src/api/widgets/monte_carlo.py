"""Monte Carlo Widget API Adapter."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import numpy as np

from api.widgets.base import BaseWidgetAdapter
from api.widgets.exceptions import WidgetDataError, WidgetValidationError
from api.schemas.widgets import MonteCarloData
from api.services.widget_cache import widget_cache
from api.services.performance_monitor import monitor_widget_performance
from widgets.monte_carlo_widget import MonteCarloWidget

logger = logging.getLogger(__name__)


class MonteCarloAdapter(BaseWidgetAdapter):
    """Adapter to expose Monte Carlo simulation widget through API."""
    
    # Monte Carlo cache TTL (20 minutes - complex calculation, occasional updates)
    CACHE_TTL_MINUTES = 20
    
    def __init__(self, storage):
        super().__init__(storage, MonteCarloWidget)
        
    def get_widget_name(self) -> str:
        return "monte_carlo"
        
    def get_widget_description(self) -> str:
        return "Monte Carlo portfolio risk simulation and scenario analysis"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate parameters for Monte Carlo simulation."""
        validated = {}
        
        # Portfolio ID is optional
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
            
        # Number of simulations
        num_simulations = kwargs.get('num_simulations', 1000)
        if not isinstance(num_simulations, (int, float)) or num_simulations < 100:
            raise WidgetValidationError("num_simulations must be at least 100")
        validated['num_simulations'] = int(min(num_simulations, 10000))  # Cap at 10k for API performance
        
        # Time horizon in days
        time_horizon_days = kwargs.get('time_horizon_days', 252)  # Default 1 year
        if not isinstance(time_horizon_days, (int, float)) or time_horizon_days <= 0:
            raise WidgetValidationError("time_horizon_days must be positive")
        validated['time_horizon_days'] = int(time_horizon_days)
        
        # Time horizon in years (for widget compatibility)
        validated['time_horizon_years'] = time_horizon_days / 252.0
        
        # Confidence level for VaR
        confidence_level = kwargs.get('confidence_level', 0.95)
        if not isinstance(confidence_level, (int, float)) or not (0.8 <= confidence_level <= 0.99):
            raise WidgetValidationError("confidence_level must be between 0.8 and 0.99")
        validated['confidence_level'] = float(confidence_level)
        
        # Initial portfolio value
        initial_value = kwargs.get('initial_value')
        if initial_value is not None:
            if not isinstance(initial_value, (int, float)) or initial_value <= 0:
                raise WidgetValidationError("initial_value must be positive")
            validated['initial_value'] = float(initial_value)
        else:
            validated['initial_value'] = None  # Will use current portfolio value
            
        # Include dividends in simulation
        include_dividends = kwargs.get('include_dividends', True)
        validated['include_dividends'] = bool(include_dividends)
        
        # Estimation method for parameters
        estimation_method = kwargs.get('estimation_method', 'Historical Mean')
        if estimation_method not in ['Historical Mean', 'Exponentially Weighted']:
            raise WidgetValidationError("estimation_method must be 'Historical Mean' or 'Exponentially Weighted'")
        validated['estimation_method'] = estimation_method
        
        # Advanced parameters
        validated['enable_contributions'] = bool(kwargs.get('enable_contributions', False))
        validated['contribution_amount'] = float(kwargs.get('contribution_amount', 0))
        validated['contribution_frequency'] = kwargs.get('contribution_frequency', 'Annual')
        
        return validated
        
    def extract_calculation_data(self, widget_instance) -> Dict[str, Any]:
        """Extract Monte Carlo simulation data from widget.
        
        This method properly delegates to the existing widget's calculation logic
        without duplicating any business logic (proper adapter pattern).
        """
        try:
            # Get instruments data from storage (same as widget does)
            instruments = self.storage.get_all_instruments()
            
            if not instruments:
                logger.warning("No instruments found for Monte Carlo simulation")
                raise WidgetDataError(
                    "No instruments found in portfolio. Please add some positions first.",
                    error_code="NO_INSTRUMENTS"
                )
                
            # Get holdings with quantities > 0 (same logic as widget)
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            
            if not holdings:
                logger.info("Portfolio exists but all positions have zero quantity")
                return self._empty_monte_carlo_response()
            
            # **DELEGATE TO EXISTING WIDGET** - Use existing calculation logic!
            try:
                simulation_results = self._calculate_monte_carlo_using_widget(
                    widget_instance, holdings, self.validated_params
                )
                
                if simulation_results is None:
                    raise WidgetDataError(
                        "Monte Carlo simulation returned no results",
                        error_code="NO_SIMULATION_DATA"
                    )
                
                # Convert existing widget data to API format
                api_response = self._convert_simulation_data_to_api_format(simulation_results)
                
            except Exception as calc_error:
                logger.error(f"Monte Carlo simulation calculation failed: {calc_error}")
                raise WidgetDataError(
                    f"Monte Carlo simulation calculation failed: {str(calc_error)}",
                    error_code="CALCULATION_ERROR"
                )
            
            return api_response
            
        except WidgetDataError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting Monte Carlo simulation: {e}", exc_info=True)
            raise WidgetDataError(
                f"Failed to extract Monte Carlo simulation: {str(e)}",
                error_code="UNEXPECTED_ERROR"
            )
    
    def _calculate_monte_carlo_using_widget(self, widget_instance, holdings: List[Dict[str, Any]], params: Dict[str, Any]):
        """Use the existing widget's calculation methods."""
        # Get symbols and basic data
        symbols = [h.get('symbol', '') for h in holdings if h.get('symbol')]
        
        if len(symbols) == 0:
            logger.warning("No valid symbols found for Monte Carlo simulation")
            return None
        
        # Use portfolio summary widget to get current portfolio metrics
        from widgets.portfolio_summary_widget import PortfolioSummaryWidget
        portfolio_widget = PortfolioSummaryWidget(self.storage, "temp_portfolio")
        
        try:
            # Get current portfolio metrics (includes current values and weights)
            metrics = portfolio_widget._calculate_all_metrics(holdings)
            if not metrics:
                logger.warning("Could not calculate current portfolio metrics")
                return None
                
            # Extract total value
            total_value = metrics.total_value
            
            if total_value <= 0:
                logger.warning(f"Portfolio total value is invalid: {total_value}")
                return None
                
            # Calculate weights from current holdings using latest prices
            latest_prices = self.storage.get_latest_prices(symbols)
            
            weights = []
            for holding in holdings:
                symbol = holding.get('symbol', '')
                if symbol in symbols:
                    quantity = holding.get('quantity', 0)
                    # Get latest price
                    price_info = latest_prices.get(symbol, {})
                    current_price = price_info.get('close', 0) if price_info else 0
                    
                    if current_price > 0:
                        market_value = quantity * current_price
                        weight = market_value / total_value if total_value > 0 else 0
                        weights.append(weight)
                    else:
                        logger.warning(f"No valid price for {symbol}")
                        weights.append(0)
            
            weights = np.array(weights)
            
            # Normalize weights to sum to 1
            if weights.sum() > 0:
                weights = weights / weights.sum()
            else:
                logger.warning("All weights are zero")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return None
        
        # Get initial value (use current portfolio value if not specified)
        initial_value = params.get('initial_value') or total_value
        
        # Get historical returns data
        try:
            # Use widget's data preparation method
            days_needed = max(730, params.get('time_horizon_days', 252) + 200)  # Minimum 2 years for stable estimates
            
            # Get returns DataFrame for all symbols
            returns_df = widget_instance._fetch_returns_data(symbols, days_needed, params.get('include_dividends', True))
            
            if returns_df is None or returns_df.empty:
                logger.warning("No returns data available for Monte Carlo simulation")
                return None
                
            # Use widget's Monte Carlo calculation method (static method)
            simulation_results = MonteCarloWidget._run_monte_carlo(
                symbols=symbols,
                weights=weights,
                returns_df=returns_df,
                num_sims=params.get('num_simulations', 1000),
                years=params.get('time_horizon_years', 1.0),
                initial_value=initial_value,
                include_dividends=params.get('include_dividends', True),
                confidence_level=int(params.get('confidence_level', 0.95) * 100),  # Widget expects int (95 not 0.95)
                estimation_method=params.get('estimation_method', 'Historical Mean'),
                enable_contributions=params.get('enable_contributions', False),
                contribution_amount=params.get('contribution_amount', 0),
                contribution_frequency=params.get('contribution_frequency', 'Annual')
            )
            
            return simulation_results
            
        except Exception as e:
            logger.error(f"Widget Monte Carlo calculation failed: {e}")
            raise
    
    def _convert_simulation_data_to_api_format(self, simulation_results) -> Dict[str, Any]:
        """Convert the existing widget's simulation results to API response format."""
        # Extract scenarios from simulation paths
        scenarios = []
        for i in range(min(len(simulation_results.final_values), 100)):  # Limit to 100 scenarios for API efficiency
            final_value = float(simulation_results.final_values[i])
            return_percent = ((final_value / simulation_results.initial_value) - 1) * 100
            
            # Calculate max drawdown for this path
            path = simulation_results.paths[i]
            running_max = np.maximum.accumulate(path)
            drawdowns = (path - running_max) / running_max
            max_drawdown = float(abs(np.min(drawdowns)) * 100)  # Convert to percentage
            
            scenarios.append({
                "final_value": final_value,
                "return_percent": return_percent,
                "max_drawdown": max_drawdown
            })
        
        # Summary statistics
        statistics = {
            "mean_final_value": float(np.mean(simulation_results.final_values)),
            "std_final_value": float(np.std(simulation_results.final_values)),
            "mean_return_percent": ((np.mean(simulation_results.final_values) / simulation_results.initial_value) - 1) * 100,
            "probability_of_loss": float(simulation_results.paths_below_initial / simulation_results.num_sims),
            "cagr_median": float(simulation_results.cagr_median),
            "cagr_10th": float(simulation_results.cagr_10th),
            "cagr_90th": float(simulation_results.cagr_90th),
            "historical_sharpe": float(simulation_results.historical_sharpe),
            "historical_volatility": float(simulation_results.historical_volatility),
            "max_drawdown_median": float(simulation_results.max_drawdown_median)
        }
        
        # Percentiles
        percentiles = {
            "10": float(simulation_results.percentile_10),
            "50": float(simulation_results.percentile_50),
            "90": float(simulation_results.percentile_90)
        }
        
        # Risk metrics
        var_95 = float(simulation_results.var_95)
        var_99 = float(getattr(simulation_results, 'var_99', simulation_results.percentile_10))  # Fallback if var_99 not available
        
        # Simulation parameters used
        simulation_params = {
            "num_simulations": int(simulation_results.num_sims),
            "time_horizon_years": float(len(simulation_results.time_points) / 252),  # Approximate
            "initial_value": float(simulation_results.initial_value),
            "confidence_level": 95  # Default for now
        }
        
        return {
            "scenarios": scenarios,
            "statistics": statistics,
            "percentiles": percentiles,
            "var_95": var_95,
            "var_99": var_99,
            "simulation_params": simulation_params,
            "execution_time_seconds": 0.0,  # Will be filled by performance monitor
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _empty_monte_carlo_response(self) -> Dict[str, Any]:
        """Return empty Monte Carlo response structure."""
        return {
            "scenarios": [],
            "statistics": {
                "mean_final_value": 0.0,
                "std_final_value": 0.0,
                "mean_return_percent": 0.0,
                "probability_of_loss": 0.0,
                "cagr_median": 0.0,
                "cagr_10th": 0.0,
                "cagr_90th": 0.0,
                "historical_sharpe": 0.0,
                "historical_volatility": 0.0,
                "max_drawdown_median": 0.0
            },
            "percentiles": {"10": 0.0, "50": 0.0, "90": 0.0},
            "var_95": 0.0,
            "var_99": 0.0,
            "simulation_params": {
                "num_simulations": 0,
                "time_horizon_years": 0.0,
                "initial_value": 0.0,
                "confidence_level": 95
            },
            "execution_time_seconds": 0.0,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute Monte Carlo simulation with caching and performance monitoring."""
        # Validate parameters
        self.validated_params = self.validate_input_parameters(**kwargs)
        
        # Check cache first
        cached_result = widget_cache.get(self.get_widget_name(), self.validated_params)
        
        if cached_result:
            logger.debug(f"Cache hit for Monte Carlo simulation")
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
                
                logger.debug(f"Monte Carlo simulation calculated and cached")
                return result
                
            except Exception as e:
                logger.error(f"Monte Carlo simulation calculation failed: {e}")
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
        """Create Monte Carlo widget instance."""
        widget_id = f"monte_carlo_{hash(str(validated_params))}"
        widget = self.widget_class(self.storage, widget_id)
        
        # Set portfolio ID if provided
        if validated_params.get('portfolio_id'):
            widget.portfolio_id = validated_params['portfolio_id']
            
        return widget