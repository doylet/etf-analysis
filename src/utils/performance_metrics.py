"""
Performance metrics calculations for portfolio analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate daily returns from price series."""
    return prices.pct_change().infer_objects(copy=False).dropna()


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.04) -> float:
    """
    Calculate Sharpe Ratio
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate (default 4%)
    
    Returns:
        Sharpe ratio (annualized)
    """
    if len(returns) == 0:
        return 0.0
    
    # Annualize the risk-free rate to daily
    daily_rf = (1 + risk_free_rate) ** (1/252) - 1
    
    excess_returns = returns - daily_rf
    
    if excess_returns.std() == 0:
        return 0.0
    
    # Annualize: sqrt(252) for daily data
    sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
    return sharpe


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.04) -> float:
    """
    Calculate Sortino Ratio (uses downside deviation instead of total volatility)
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate (default 4%)
    
    Returns:
        Sortino ratio (annualized)
    """
    if len(returns) == 0:
        return 0.0
    
    daily_rf = (1 + risk_free_rate) ** (1/252) - 1
    excess_returns = returns - daily_rf
    
    # Only consider downside returns
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0
    
    sortino = (excess_returns.mean() / downside_returns.std()) * np.sqrt(252)
    return sortino


def calculate_omega_ratio(returns: pd.Series, threshold: float = 0.0) -> float:
    """
    Calculate Omega Ratio (probability-weighted ratio of gains to losses)
    
    Args:
        returns: Series of returns
        threshold: Minimum acceptable return (default 0%)
    
    Returns:
        Omega ratio
    """
    if len(returns) == 0:
        return 0.0
    
    gains = returns[returns > threshold] - threshold
    losses = threshold - returns[returns < threshold]
    
    if losses.sum() == 0:
        return np.inf if gains.sum() > 0 else 0.0
    
    omega = gains.sum() / losses.sum()
    return omega


def calculate_irr(cash_flows: List[Tuple[datetime, float]]) -> float:
    """
    Calculate Internal Rate of Return (IRR)
    
    Args:
        cash_flows: List of (date, amount) tuples. Negative for investments, positive for returns.
    
    Returns:
        IRR as decimal (e.g., 0.15 for 15%)
    """
    if len(cash_flows) < 2:
        return 0.0
    
    # Sort by date
    cash_flows = sorted(cash_flows, key=lambda x: x[0])
    
    # Calculate days from first cash flow
    start_date = cash_flows[0][0]
    
    def npv(rate):
        """Calculate NPV at given rate"""
        total = 0.0
        for date, amount in cash_flows:
            days = (date - start_date).days
            years = days / 365.25
            total += amount / ((1 + rate) ** years)
        return total
    
    # Use Newton's method to find IRR
    rate = 0.1  # Initial guess
    for _ in range(100):
        npv_val = npv(rate)
        if abs(npv_val) < 0.01:
            break
        
        # Calculate derivative
        derivative = 0.0
        for date, amount in cash_flows:
            days = (date - start_date).days
            years = days / 365.25
            derivative -= years * amount / ((1 + rate) ** (years + 1))
        
        if abs(derivative) < 1e-10:
            break
        
        rate = rate - npv_val / derivative
    
    return rate


def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    Calculate maximum drawdown
    
    Args:
        prices: Series of prices
    
    Returns:
        Maximum drawdown as decimal (e.g., -0.25 for -25%)
    """
    if len(prices) == 0:
        return 0.0
    
    # Calculate cumulative returns
    cum_returns = (1 + prices.pct_change()).cumprod()
    running_max = cum_returns.expanding().max()
    drawdown = (cum_returns - running_max) / running_max
    
    return drawdown.min()


def calculate_beta(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Calculate beta relative to benchmark
    
    Args:
        returns: Portfolio returns
        benchmark_returns: Benchmark returns
    
    Returns:
        Beta coefficient
    """
    if len(returns) == 0 or len(benchmark_returns) == 0:
        return 0.0
    
    # Align the series
    df = pd.DataFrame({'portfolio': returns, 'benchmark': benchmark_returns}).dropna()
    
    if len(df) < 2:
        return 0.0
    
    covariance = df['portfolio'].cov(df['benchmark'])
    benchmark_variance = df['benchmark'].var()
    
    if benchmark_variance == 0:
        return 0.0
    
    return covariance / benchmark_variance


def calculate_alpha(returns: pd.Series, benchmark_returns: pd.Series, 
                    risk_free_rate: float = 0.04) -> float:
    """
    Calculate alpha (Jensen's alpha)
    
    Args:
        returns: Portfolio returns
        benchmark_returns: Benchmark returns
        risk_free_rate: Annual risk-free rate
    
    Returns:
        Alpha (annualized)
    """
    if len(returns) == 0 or len(benchmark_returns) == 0:
        return 0.0
    
    # Calculate beta
    beta = calculate_beta(returns, benchmark_returns)
    
    # Annualize returns
    portfolio_return = returns.mean() * 252
    benchmark_return = benchmark_returns.mean() * 252
    
    # Jensen's alpha
    alpha = portfolio_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))
    
    return alpha


def calculate_information_ratio(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Calculate Information Ratio (excess return per unit of tracking error)
    
    Args:
        returns: Portfolio returns
        benchmark_returns: Benchmark returns
    
    Returns:
        Information ratio (annualized)
    """
    if len(returns) == 0 or len(benchmark_returns) == 0:
        return 0.0
    
    # Align the series
    df = pd.DataFrame({'portfolio': returns, 'benchmark': benchmark_returns}).dropna()
    
    if len(df) < 2:
        return 0.0
    
    excess_returns = df['portfolio'] - df['benchmark']
    tracking_error = excess_returns.std()
    
    if tracking_error == 0:
        return 0.0
    
    # Annualize
    ir = (excess_returns.mean() / tracking_error) * np.sqrt(252)
    
    return ir


def calculate_money_weighted_return(cash_flows: List[Tuple[datetime, float]], 
                                     current_value: float) -> float:
    """
    Calculate money-weighted return (simple return based on cash invested)
    
    Args:
        cash_flows: List of (date, amount) tuples. Negative for investments.
        current_value: Current portfolio value
    
    Returns:
        Simple return as decimal (e.g., 0.15 for 15%)
    """
    if not cash_flows:
        return 0.0
    
    # Sum all negative cash flows (investments)
    total_invested = sum(abs(cf) for _, cf in cash_flows if cf < 0)
    
    # Sum all positive cash flows (withdrawals/sales)
    total_withdrawn = sum(cf for _, cf in cash_flows if cf > 0)
    
    if total_invested == 0:
        return 0.0
    
    # Net profit = current value + withdrawals - investments
    net_profit = current_value + total_withdrawn - total_invested
    
    return net_profit / total_invested


def calculate_time_weighted_return(prices: pd.Series, cash_flow_dates: List[datetime]) -> float:
    """
    Calculate time-weighted return (accounts for timing of cash flows)
    
    Args:
        prices: Series of portfolio values over time
        cash_flow_dates: Dates when cash flows occurred
    
    Returns:
        Time-weighted return as decimal
    """
    if len(prices) < 2:
        return 0.0
    
    if not cash_flow_dates:
        # No cash flows, simple return
        return (prices.iloc[-1] / prices.iloc[0]) - 1
    
    # Split portfolio into sub-periods around cash flows
    sub_returns = []
    
    # Convert dates to pandas Timestamps for comparison
    cf_dates = [pd.Timestamp(d) for d in cash_flow_dates]
    cf_dates = sorted(set(cf_dates))  # Remove duplicates and sort
    
    # Get price index dates
    price_dates = prices.index
    
    prev_date = price_dates[0]
    
    for cf_date in cf_dates:
        # Find prices before and after cash flow
        before_prices = prices[prices.index <= cf_date]
        
        if len(before_prices) > 0 and before_prices.index[-1] > prev_date:
            # Calculate return for this sub-period
            start_price = prices.loc[prev_date]
            end_price = before_prices.iloc[-1]
            
            if start_price > 0:
                sub_return = end_price / start_price
                sub_returns.append(sub_return)
            
            prev_date = before_prices.index[-1]
    
    # Final period from last cash flow to end
    if prev_date < price_dates[-1]:
        start_price = prices.loc[prev_date]
        end_price = prices.iloc[-1]
        
        if start_price > 0:
            sub_return = end_price / start_price
            sub_returns.append(sub_return)
    
    if not sub_returns:
        return (prices.iloc[-1] / prices.iloc[0]) - 1
    
    # Compound all sub-period returns
    cumulative_return = 1.0
    for sr in sub_returns:
        cumulative_return *= sr
    
    return cumulative_return - 1


def calculate_dividend_yield(dividends_received: float, average_portfolio_value: float) -> float:
    """
    Calculate dividend yield as percentage
    
    Args:
        dividends_received: Total dividends received in period
        average_portfolio_value: Average portfolio value during period
    
    Returns:
        Dividend yield as decimal (e.g., 0.03 for 3%)
    """
    if average_portfolio_value == 0:
        return 0.0
    
    return dividends_received / average_portfolio_value


def calculate_total_return_with_dividends(price_return: float, dividend_return: float) -> float:
    """
    Calculate total return including price appreciation and dividends
    
    Args:
        price_return: Return from price changes (as decimal)
        dividend_return: Return from dividends (as decimal)
    
    Returns:
        Total return as decimal
    """
    # Compound the returns
    return (1 + price_return) * (1 + dividend_return) - 1
