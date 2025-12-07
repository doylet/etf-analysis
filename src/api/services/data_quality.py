"""Data quality assessment service for widget calculations."""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataQualityMetrics:
    """Data quality metrics for a dataset."""
    completeness_score: float  # 0-1, percentage of non-null values
    freshness_score: float     # 0-1, how recent the data is 
    accuracy_score: float      # 0-1, data validation checks passed
    consistency_score: float   # 0-1, internal consistency checks
    overall_score: float       # 0-1, weighted average
    issues: List[str]          # List of data quality issues found
    last_updated: datetime     # When data was last refreshed
    record_count: int          # Number of records assessed


class DataQualityService:
    """Service for assessing data quality for widget calculations."""
    
    def __init__(self):
        self.freshness_threshold_hours = 24  # Data older than this is considered stale
        self.completeness_threshold = 0.95   # Minimum acceptable completeness
        self.accuracy_threshold = 0.90       # Minimum acceptable accuracy
        
    def assess_portfolio_data_quality(self, 
                                    portfolio_data: Dict[str, Any],
                                    price_data: Optional[Dict[str, Any]] = None) -> DataQualityMetrics:
        """Assess data quality for portfolio analysis.
        
        Args:
            portfolio_data: Portfolio positions and transaction data
            price_data: Market price data for assets
            
        Returns:
            DataQualityMetrics with assessment results
        """
        issues = []
        
        # Check portfolio data completeness
        completeness_score = self._assess_completeness(portfolio_data, issues)
        
        # Check data freshness
        freshness_score = self._assess_freshness(portfolio_data, price_data, issues)
        
        # Check data accuracy
        accuracy_score = self._assess_accuracy(portfolio_data, issues)
        
        # Check data consistency
        consistency_score = self._assess_consistency(portfolio_data, issues)
        
        # Calculate overall score (weighted average)
        overall_score = (
            completeness_score * 0.3 +
            freshness_score * 0.3 +
            accuracy_score * 0.2 +
            consistency_score * 0.2
        )
        
        return DataQualityMetrics(
            completeness_score=completeness_score,
            freshness_score=freshness_score,
            accuracy_score=accuracy_score,
            consistency_score=consistency_score,
            overall_score=overall_score,
            issues=issues,
            last_updated=datetime.utcnow(),
            record_count=self._count_records(portfolio_data)
        )
        
    def _assess_completeness(self, data: Dict[str, Any], issues: List[str]) -> float:
        """Assess data completeness - percentage of non-null required fields."""
        if not data:
            issues.append("Portfolio data is empty")
            return 0.0
            
        required_fields = ['positions', 'cash', 'total_value']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            issues.append(f"Missing required fields: {', '.join(missing_fields)}")
            
        # Check position data completeness
        positions = data.get('positions', [])
        if not positions:
            issues.append("No positions found in portfolio")
            return 0.0
            
        position_field_completeness = []
        required_position_fields = ['symbol', 'quantity', 'current_price', 'market_value']
        
        for position in positions:
            if isinstance(position, dict):
                missing_pos_fields = [
                    field for field in required_position_fields 
                    if field not in position or position[field] is None
                ]
                completeness = 1.0 - (len(missing_pos_fields) / len(required_position_fields))
                position_field_completeness.append(completeness)
                
        avg_position_completeness = (
            sum(position_field_completeness) / len(position_field_completeness) 
            if position_field_completeness else 0.0
        )
        
        portfolio_completeness = 1.0 - (len(missing_fields) / len(required_fields))
        overall_completeness = (portfolio_completeness + avg_position_completeness) / 2
        
        if overall_completeness < self.completeness_threshold:
            issues.append(f"Data completeness {overall_completeness:.2%} below threshold {self.completeness_threshold:.2%}")
            
        return overall_completeness
        
    def _assess_freshness(self, portfolio_data: Dict[str, Any], 
                         price_data: Optional[Dict[str, Any]], issues: List[str]) -> float:
        """Assess data freshness - how recent the data is."""
        now = datetime.utcnow()
        freshness_scores = []
        
        # Check portfolio data timestamp
        last_updated = portfolio_data.get('last_updated')
        if last_updated:
            if isinstance(last_updated, str):
                try:
                    last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                except ValueError:
                    issues.append("Invalid last_updated timestamp format")
                    return 0.0
                    
            hours_old = (now - last_updated).total_seconds() / 3600
            portfolio_freshness = max(0.0, 1.0 - (hours_old / self.freshness_threshold_hours))
            freshness_scores.append(portfolio_freshness)
            
            if hours_old > self.freshness_threshold_hours:
                issues.append(f"Portfolio data is {hours_old:.1f} hours old (threshold: {self.freshness_threshold_hours})")
        else:
            issues.append("Portfolio data missing last_updated timestamp")
            freshness_scores.append(0.0)
            
        # Check price data freshness if provided
        if price_data:
            for symbol, price_info in price_data.items():
                if isinstance(price_info, dict) and 'timestamp' in price_info:
                    try:
                        price_timestamp = datetime.fromisoformat(price_info['timestamp'].replace('Z', '+00:00'))
                        hours_old = (now - price_timestamp).total_seconds() / 3600
                        price_freshness = max(0.0, 1.0 - (hours_old / self.freshness_threshold_hours))
                        freshness_scores.append(price_freshness)
                    except (ValueError, KeyError):
                        issues.append(f"Invalid price timestamp for {symbol}")
                        
        return sum(freshness_scores) / len(freshness_scores) if freshness_scores else 0.0
        
    def _assess_accuracy(self, data: Dict[str, Any], issues: List[str]) -> float:
        """Assess data accuracy - validation checks."""
        accuracy_checks = []
        
        # Check for negative values where inappropriate
        if 'total_value' in data and data['total_value'] is not None:
            if data['total_value'] < 0:
                issues.append("Total portfolio value is negative")
                accuracy_checks.append(0.0)
            else:
                accuracy_checks.append(1.0)
                
        # Check cash position
        if 'cash' in data and data['cash'] is not None:
            if data['cash'] < 0:
                issues.append("Cash position is negative (margin not supported)")
                accuracy_checks.append(0.0)
            else:
                accuracy_checks.append(1.0)
                
        # Check position data accuracy
        positions = data.get('positions', [])
        position_accuracy = []
        
        for i, position in enumerate(positions):
            if not isinstance(position, dict):
                issues.append(f"Position {i} is not a dictionary")
                position_accuracy.append(0.0)
                continue
                
            pos_checks = []
            
            # Check quantity
            quantity = position.get('quantity', 0)
            if quantity <= 0:
                issues.append(f"Position {position.get('symbol', i)} has invalid quantity: {quantity}")
                pos_checks.append(0.0)
            else:
                pos_checks.append(1.0)
                
            # Check price
            price = position.get('current_price', 0)
            if price <= 0:
                issues.append(f"Position {position.get('symbol', i)} has invalid price: {price}")
                pos_checks.append(0.0)  
            else:
                pos_checks.append(1.0)
                
            # Check market value calculation
            market_value = position.get('market_value', 0)
            expected_value = quantity * price
            if abs(market_value - expected_value) > 0.01:  # Allow for rounding
                issues.append(f"Position {position.get('symbol', i)} market value mismatch")
                pos_checks.append(0.0)
            else:
                pos_checks.append(1.0)
                
            position_accuracy.append(sum(pos_checks) / len(pos_checks) if pos_checks else 0.0)
            
        if position_accuracy:
            accuracy_checks.append(sum(position_accuracy) / len(position_accuracy))
            
        overall_accuracy = sum(accuracy_checks) / len(accuracy_checks) if accuracy_checks else 0.0
        
        if overall_accuracy < self.accuracy_threshold:
            issues.append(f"Data accuracy {overall_accuracy:.2%} below threshold {self.accuracy_threshold:.2%}")
            
        return overall_accuracy
        
    def _assess_consistency(self, data: Dict[str, Any], issues: List[str]) -> float:
        """Assess internal data consistency."""
        consistency_checks = []
        
        # Check if total value matches sum of positions + cash
        positions = data.get('positions', [])
        cash = data.get('cash', 0)
        total_value = data.get('total_value', 0)
        
        if positions and total_value > 0:
            calculated_total = cash + sum(
                pos.get('market_value', 0) 
                for pos in positions 
                if isinstance(pos, dict)
            )
            
            # Allow 1% variance for rounding/timing differences
            variance = abs(total_value - calculated_total) / total_value
            if variance > 0.01:
                issues.append(f"Total value inconsistency: reported={total_value}, calculated={calculated_total}")
                consistency_checks.append(0.0)
            else:
                consistency_checks.append(1.0)
                
        # Check for duplicate positions
        symbols = []
        for position in positions:
            if isinstance(position, dict) and 'symbol' in position:
                symbol = position['symbol']
                if symbol in symbols:
                    issues.append(f"Duplicate position found for symbol: {symbol}")
                    consistency_checks.append(0.0)
                else:
                    symbols.append(symbol)
                    consistency_checks.append(1.0)
                    
        return sum(consistency_checks) / len(consistency_checks) if consistency_checks else 1.0
        
    def _count_records(self, data: Dict[str, Any]) -> int:
        """Count number of data records."""
        positions = data.get('positions', [])
        return len(positions) if positions else 0
        
    def validate_for_calculation(self, data_quality: DataQualityMetrics) -> Tuple[bool, List[str]]:
        """Determine if data quality is sufficient for reliable calculations.
        
        Args:
            data_quality: Data quality assessment results
            
        Returns:
            Tuple of (is_valid, list_of_blocking_issues)
        """
        blocking_issues = []
        
        if data_quality.overall_score < 0.7:
            blocking_issues.append(f"Overall data quality too low: {data_quality.overall_score:.2%}")
            
        if data_quality.completeness_score < 0.8:
            blocking_issues.append(f"Data completeness too low: {data_quality.completeness_score:.2%}")
            
        if data_quality.accuracy_score < 0.8:
            blocking_issues.append(f"Data accuracy too low: {data_quality.accuracy_score:.2%}")
            
        if data_quality.record_count == 0:
            blocking_issues.append("No data records found")
            
        return len(blocking_issues) == 0, blocking_issues


# Global service instance
data_quality_service = DataQualityService()