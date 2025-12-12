"""Performance Widget API Adapter."""

from typing import Dict, Any
import logging

from src.api.widgets.base import BaseWidgetAdapter
from src.api.widgets.exceptions import WidgetValidationError
from src.widgets.performance_widget import PerformanceWidget

logger = logging.getLogger(__name__)


class PerformanceAdapter(BaseWidgetAdapter):
    """Adapter to expose performance widget through API."""
    
    def __init__(self, storage):
        super().__init__(storage, PerformanceWidget)
        
    def get_widget_name(self) -> str:
        return "performance"
        
    def get_widget_description(self) -> str:
        return "Analyze portfolio performance metrics and statistics"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        validated = {}
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
        
        # Time period mapping
        period_map = {
            '1W': 7, '1M': 30, '3M': 90, '6M': 180, 
            '1Y': 365, '2Y': 730, '5Y': 1825
        }
        time_period = kwargs.get('time_period', '1Y')
        validated['period_days'] = period_map.get(time_period, 365)
        
        return validated
        
    def extract_calculation_data(self, widget_instance, validated_params: Dict[str, Any] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        import pandas as pd
        import numpy as np
        from src.utils.performance_metrics import calculate_returns, calculate_sharpe_ratio
        
        try:
            # Get parameters from validated_params or use defaults
            period_days = validated_params.get('period_days', 365) if validated_params else 365
            
            instruments = self.storage.get_all_instruments()
            if not instruments:
                return {"message": "No instruments available"}
            
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            if not holdings:
                return {"message": "No active holdings"}
            
            # Get symbols and calculate performance
            symbols = [h['symbol'] for h in holdings]
            
            # Fetch performance data using widget's method
            performance_metrics = widget_instance._fetch_performance_data(symbols, period_days)
            
            if not performance_metrics:
                return {"message": "No price data available for selected period"}
            
            # Calculate aggregate portfolio metrics from individual holdings
            total_change_pct = sum(m.change_pct for m in performance_metrics) / len(performance_metrics)
            
            # Calculate portfolio-level metrics using cost basis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Get current portfolio values with cost basis
            # Import the portfolio calculation logic
            import sqlite3
            
            # Get latest prices
            symbols = [h['symbol'] for h in holdings]
            latest_prices_data = self.storage.get_latest_prices(symbols)
            latest_prices = {}
            for symbol, data in latest_prices_data.items():
                if isinstance(data, dict) and 'close' in data:
                    latest_prices[symbol] = float(data['close'])
                else:
                    latest_prices[symbol] = 0.0
            
            # Get latest AUD/USD exchange rate
            conn = sqlite3.connect('data/etf_analysis.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT rate FROM fx_rates WHERE currency_pair = 'AUDUSD' ORDER BY date DESC LIMIT 1"
            )
            fx_result = cursor.fetchone()
            audusd_rate = float(fx_result[0]) if fx_result else 0.655
            usd_to_aud = 1 / audusd_rate
            
            # Calculate total current value and cost basis
            total_current_value = 0.0
            total_cost_basis = 0.0
            portfolio_values = []  # For volatility calculation
            
            for holding in holdings:
                symbol = holding['symbol']
                quantity = holding.get('quantity', 0)
                currency = holding.get('currency', 'USD')
                
                if quantity <= 0:
                    continue
                
                # Get orders for cost basis calculation
                orders = self.storage.get_orders(symbol)
                
                # Calculate weighted average cost
                total_spent = 0.0
                total_shares = 0.0
                
                for order in orders:
                    order_type = str(order.get('order_type', '')).upper()
                    volume = order.get('volume', 0)
                    order_date_str = order.get('order_date')
                    
                    if not order_date_str or volume <= 0:
                        continue
                    
                    # Parse order date
                    try:
                        order_date = pd.to_datetime(order_date_str)
                    except:
                        continue
                    
                    # Get price at order date
                    price_df = self.storage.get_price_data(symbol, order_date, order_date + timedelta(days=5))
                    
                    if price_df is not None and not price_df.empty:
                        close_price = float(price_df['close'].iloc[0])
                        
                        # Convert to AUD if needed
                        if currency == 'USD':
                            # Get historical FX rate
                            cursor.execute(
                                "SELECT rate FROM fx_rates WHERE currency_pair = 'AUDUSD' AND date <= ? ORDER BY date DESC LIMIT 1",
                                (order_date.strftime('%Y-%m-%d'),)
                            )
                            hist_fx = cursor.fetchone()
                            hist_usd_to_aud = 1 / float(hist_fx[0]) if hist_fx else usd_to_aud
                            close_price = close_price * hist_usd_to_aud
                        
                        if order_type == 'BUY':
                            total_spent += volume * close_price
                            total_shares += volume
                        elif order_type == 'SELL':
                            if total_shares > 0:
                                avg_cost_so_far = total_spent / total_shares
                                total_spent -= volume * avg_cost_so_far
                                total_shares -= volume
                
                # Calculate position values
                # Use total_spent directly since it already represents the remaining cost basis
                # and total_shares should equal quantity after processing all orders
                current_price = latest_prices.get(symbol, 0.0)
                
                # Convert current price to AUD
                if currency == 'USD':
                    current_price = current_price * usd_to_aud
                
                position_current_value = quantity * current_price
                # Use total_spent as the cost basis for current holdings
                position_cost_basis = total_spent
                
                total_current_value += position_current_value
                total_cost_basis += position_cost_basis
                
                # Also collect time series for volatility
                price_df = self.storage.get_price_data(symbol, start_date, end_date)
                if price_df is not None and not price_df.empty:
                    position_values = price_df['close'] * quantity
                    if currency == 'USD':
                        position_values = position_values * usd_to_aud
                    portfolio_values.append(position_values)
            
            conn.close()
            
            # Calculate returns based on actual cost basis
            if total_cost_basis > 0:
                total_return = ((total_current_value - total_cost_basis) / total_cost_basis) * 100
                
                # Calculate annualized return
                years = period_days / 365.0
                if years > 0 and total_return > -100:
                    annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100
                else:
                    annualized_return = 0.0
                
                # Calculate volatility from time series if available
                if portfolio_values:
                    total_portfolio_value = pd.concat(portfolio_values, axis=1).sum(axis=1)
                    portfolio_returns_series = calculate_returns(total_portfolio_value)
                    volatility = portfolio_returns_series.std() * np.sqrt(252) * 100
                    sharpe = calculate_sharpe_ratio(portfolio_returns_series)
                else:
                    volatility = 0.0
                    sharpe = 0.0
            else:
                total_return = total_change_pct
                annualized_return = total_change_pct
                volatility = 0.0
                sharpe = 0.0
            
            return {
                "total_return": float(total_return),
                "annualized_return": float(annualized_return),
                "volatility": float(volatility),
                "sharpe_ratio": float(sharpe),
                "holdings_analyzed": len(performance_metrics),
                "period_days": period_days
            }
        except Exception as e:
            logger.error(f"Performance extraction failed: {e}")
            return {"error": str(e)}
    
