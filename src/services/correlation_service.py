"""
Correlation analysis service - framework-agnostic business logic.

This service provides correlation calculation functionality without any
UI framework dependencies, following the clean architecture pattern.
"""

import pandas as pd
import numpy as np
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CorrelationAnalysis:
    """Results from correlation analysis calculations."""
    correlation_matrix: pd.DataFrame
    pairs_df: pd.DataFrame
    benchmark_pivot: Optional[pd.DataFrame]
    avg_correlation: float
    max_correlation: float
    min_correlation: float
    num_days: int
    start_date: datetime
    end_date: datetime


class CorrelationService:
    """
    Service for calculating correlation analysis between financial instruments.
    
    This service provides pure business logic for correlation calculations,
    with no dependencies on UI frameworks or data storage implementations.
    """
    
    def calculate_correlation_analysis(
        self,
        returns_df: pd.DataFrame,
        selected_holdings: List[str],
        selected_additional: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> CorrelationAnalysis:
        """
        Calculate complete correlation analysis.
        
        Args:
            returns_df: DataFrame of returns for all symbols
            selected_holdings: Holdings symbols to include
            selected_additional: Additional symbols (benchmarks) to include
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            CorrelationAnalysis with correlation matrix, pairs, statistics
            
        Raises:
            ValueError: If returns_df is empty or has insufficient data
        """
        if returns_df.empty:
            raise ValueError("Returns dataframe cannot be empty")
        
        if len(returns_df) < 2:
            raise ValueError("Need at least 2 data points for correlation analysis")
        
        # Calculate correlation matrix
        correlation_matrix = returns_df.corr()
        
        # Calculate correlation statistics
        corr_values = self._extract_correlation_values(correlation_matrix)
        avg_corr = float(np.mean(corr_values)) if corr_values else 0.0
        max_corr = float(np.max(corr_values)) if corr_values else 0.0
        min_corr = float(np.min(corr_values)) if corr_values else 0.0
        
        # Calculate pairs
        pairs_df = self._calculate_correlation_pairs(correlation_matrix)
        
        # Calculate benchmark comparison if applicable
        benchmark_pivot = None
        if selected_holdings and selected_additional:
            benchmark_pivot = self._calculate_benchmark_comparison(
                correlation_matrix, selected_holdings, selected_additional, returns_df.columns
            )
        
        return CorrelationAnalysis(
            correlation_matrix=correlation_matrix,
            pairs_df=pairs_df,
            benchmark_pivot=benchmark_pivot,
            avg_correlation=avg_corr,
            max_correlation=max_corr,
            min_correlation=min_corr,
            num_days=len(returns_df),
            start_date=start_date,
            end_date=end_date
        )
    
    def _extract_correlation_values(self, correlation_matrix: pd.DataFrame) -> List[float]:
        """
        Extract unique correlation values from matrix (upper triangle).
        
        Args:
            correlation_matrix: Correlation matrix DataFrame
            
        Returns:
            List of correlation values from upper triangle
        """
        corr_values = []
        for i in range(len(correlation_matrix)):
            for j in range(i + 1, len(correlation_matrix)):
                corr_values.append(correlation_matrix.iloc[i, j])
        return corr_values
    
    def _calculate_correlation_pairs(self, correlation_matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Extract and sort correlation pairs from matrix.
        
        Args:
            correlation_matrix: Correlation matrix DataFrame
            
        Returns:
            DataFrame with 'Pair' and 'Correlation' columns, sorted by correlation (descending)
        """
        pairs = []
        for i in range(len(correlation_matrix)):
            for j in range(i + 1, len(correlation_matrix)):
                pairs.append({
                    'Pair': f"{correlation_matrix.index[i]} - {correlation_matrix.columns[j]}",
                    'Correlation': correlation_matrix.iloc[i, j]
                })
        
        if not pairs:
            return pd.DataFrame(columns=['Pair', 'Correlation'])
        
        return pd.DataFrame(pairs).sort_values('Correlation', ascending=False)
    
    def _calculate_benchmark_comparison(
        self,
        correlation_matrix: pd.DataFrame,
        holdings: List[str],
        benchmarks: List[str],
        available_columns: pd.Index
    ) -> Optional[pd.DataFrame]:
        """
        Calculate portfolio holdings vs benchmarks correlation table.
        
        Args:
            correlation_matrix: Correlation matrix
            holdings: Holding symbols to compare
            benchmarks: Benchmark symbols to compare against
            available_columns: Available columns in correlation matrix
            
        Returns:
            Pivoted DataFrame with holdings as rows, benchmarks as columns, or None if no data
        """
        benchmark_corr = []
        
        for holding in holdings:
            if holding not in available_columns:
                continue
            for benchmark in benchmarks:
                if benchmark not in available_columns:
                    continue
                benchmark_corr.append({
                    'Holding': holding,
                    'Benchmark': benchmark,
                    'Correlation': correlation_matrix.loc[holding, benchmark]
                })
        
        if not benchmark_corr:
            return None
        
        benchmark_df = pd.DataFrame(benchmark_corr)
        return benchmark_df.pivot(index='Holding', columns='Benchmark', values='Correlation')
    
    def calculate_portfolio_aggregate_correlation(
        self,
        returns_df: pd.DataFrame,
        holdings: List[str],
        weights: List[float],
        benchmarks: List[str]
    ) -> pd.DataFrame:
        """
        Calculate correlation of weighted portfolio aggregate vs benchmarks.
        
        Args:
            returns_df: DataFrame of returns for all symbols
            holdings: List of holding symbols
            weights: Corresponding weights for each holding
            benchmarks: List of benchmark symbols to compare against
            
        Returns:
            DataFrame with benchmark correlations to the portfolio
            
        Raises:
            ValueError: If holdings and weights don't match, or if data is insufficient
        """
        if len(holdings) != len(weights):
            raise ValueError("Holdings and weights must have the same length")
        
        if not holdings:
            raise ValueError("Must provide at least one holding")
        
        # Verify all symbols exist in returns_df
        missing_holdings = [h for h in holdings if h not in returns_df.columns]
        if missing_holdings:
            raise ValueError(f"Holdings not found in returns data: {missing_holdings}")
        
        missing_benchmarks = [b for b in benchmarks if b not in returns_df.columns]
        if missing_benchmarks:
            raise ValueError(f"Benchmarks not found in returns data: {missing_benchmarks}")
        
        # Calculate weighted portfolio returns
        portfolio_returns = pd.Series(0.0, index=returns_df.index)
        for holding, weight in zip(holdings, weights):
            portfolio_returns += returns_df[holding] * weight
        
        # Calculate correlations with benchmarks
        correlations = []
        for benchmark in benchmarks:
            corr = portfolio_returns.corr(returns_df[benchmark])
            correlations.append({
                'Benchmark': benchmark,
                'Correlation': corr
            })
        
        return pd.DataFrame(correlations).sort_values('Correlation', ascending=False)
