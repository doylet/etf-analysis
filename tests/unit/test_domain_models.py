"""
Unit tests for domain models.

Tests validation logic, JSON serialization, and business rules for all domain models.
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
import numpy as np

from src.domain.simulation import SimulationParameters, SimulationResults
from src.domain.optimization import (
    OptimizationRequest, 
    OptimizationResults, 
    OptimizationObjective
)
from src.domain.rebalancing import RebalancingRecommendation
from src.domain.news import SurpriseEvent, NewsArticle, EventNewsCorrelation, EventType
from src.domain.portfolio import (
    PortfolioSummary,
    InstrumentDomainModel,
    OrderRecord,
    PriceHistory,
    InstrumentType,
    OrderType
)


class TestSimulationParameters:
    """Tests for SimulationParameters domain model."""
    
    def test_valid_parameters(self):
        """Test creating valid simulation parameters."""
        params = SimulationParameters(
            symbols=["SPY", "AGG", "VTI"],
            weights=[0.5, 0.3, 0.2],
            years=10,
            num_simulations=1000,
            initial_value=100000
        )
        
        assert params.symbols == ["SPY", "AGG", "VTI"]
        assert params.weights == [0.5, 0.3, 0.2]
        assert params.years == 10
        assert params.num_simulations == 1000
        assert params.initial_value == 100000
    
    def test_weights_must_sum_to_one(self):
        """Test that weights must sum to 1.0."""
        with pytest.raises(ValidationError) as exc_info:
            SimulationParameters(
                symbols=["SPY", "AGG"],
                weights=[0.6, 0.5],  # Sum = 1.1
                years=5,
                num_simulations=100,
                initial_value=10000
            )
        
        assert "sum to 1.0" in str(exc_info.value).lower()
    
    def test_symbols_and_weights_same_length(self):
        """Test that symbols and weights must have same length."""
        with pytest.raises(ValidationError) as exc_info:
            SimulationParameters(
                symbols=["SPY", "AGG", "VTI"],
                weights=[0.5, 0.5],  # Wrong length
                years=5,
                num_simulations=100,
                initial_value=10000
            )
        
        assert "same length" in str(exc_info.value).lower()
    
    def test_negative_years_rejected(self):
        """Test that negative years are rejected."""
        with pytest.raises(ValidationError):
            SimulationParameters(
                symbols=["SPY"],
                weights=[1.0],
                years=-5,  # Invalid
                num_simulations=100,
                initial_value=10000
            )
    
    def test_num_simulations_bounds(self):
        """Test num_simulations must be within bounds."""
        # Too few
        with pytest.raises(ValidationError):
            SimulationParameters(
                symbols=["SPY"],
                weights=[1.0],
                years=5,
                num_simulations=50,  # < 100
                initial_value=10000
            )
        
        # Too many
        with pytest.raises(ValidationError):
            SimulationParameters(
                symbols=["SPY"],
                weights=[1.0],
                years=5,
                num_simulations=60000,  # > 50000
                initial_value=10000
            )
    
    def test_json_serialization(self):
        """Test JSON serialization round-trip."""
        params = SimulationParameters(
            symbols=["SPY", "AGG"],
            weights=[0.6, 0.4],
            years=10,
            num_simulations=1000,
            initial_value=100000,
            enable_contributions=True,
            contribution_amount=5000,
            contribution_frequency="Annual"
        )
        
        # Serialize to JSON
        json_str = params.to_json()
        
        # Deserialize back
        params_restored = SimulationParameters.from_json(json_str)
        
        assert params_restored.symbols == params.symbols
        assert params_restored.weights == params.weights
        assert params_restored.enable_contributions == params.enable_contributions
        assert params_restored.contribution_amount == params.contribution_amount


class TestSimulationResults:
    """Tests for SimulationResults domain model."""
    
    def test_valid_results(self):
        """Test creating valid simulation results."""
        paths = np.random.rand(100, 253) * 100000  # 100 simulations, 253 time points
        time_points = np.linspace(0, 1, 253)
        percentiles = {
            5: np.percentile(paths, 5, axis=0),
            50: np.percentile(paths, 50, axis=0),
            95: np.percentile(paths, 95, axis=0)
        }
        
        results = SimulationResults(
            paths=paths,
            time_points=time_points,
            percentiles=percentiles,
            final_values=paths[:, -1],
            var_95=50000,
            cvar_95=45000,
            max_drawdown_median=-15.5,
            cagr_median=7.2,
            cagr_10th=3.1,
            cagr_90th=11.8,
            historical_sharpe=1.2,
            historical_volatility=0.15
        )
        
        assert results.paths.shape == (100, 253)
        assert len(results.time_points) == 253
        assert 5 in results.percentiles
        assert results.var_95 == 50000
        assert results.historical_sharpe == 1.2


class TestOptimizationRequest:
    """Tests for OptimizationRequest domain model."""
    
    def test_valid_request(self):
        """Test creating valid optimization request."""
        request = OptimizationRequest(
            symbols=["SPY", "AGG", "GLD"],
            objective=OptimizationObjective.MAX_SHARPE,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2023, 12, 31)
        )
        
        assert len(request.symbols) == 3
        assert request.objective == OptimizationObjective.MAX_SHARPE
        assert request.risk_free_rate == 0.04  # Default
    
    def test_minimum_two_symbols(self):
        """Test that at least 2 symbols are required."""
        with pytest.raises(ValidationError) as exc_info:
            OptimizationRequest(
                symbols=["SPY"],  # Only 1 symbol
                objective=OptimizationObjective.MAX_SHARPE
            )
        
        assert "at least 2" in str(exc_info.value).lower()
    
    def test_constraint_validation(self):
        """Test constraint validation."""
        # Valid constraints
        request = OptimizationRequest(
            symbols=["SPY", "AGG"],
            objective=OptimizationObjective.MIN_VOLATILITY,
            constraints={"min_weight": 0.1, "max_weight": 0.6}
        )
        assert request.constraints["min_weight"] == 0.1
        
        # Invalid constraints (min > max)
        with pytest.raises(ValidationError):
            OptimizationRequest(
                symbols=["SPY", "AGG"],
                objective=OptimizationObjective.MIN_VOLATILITY,
                constraints={"min_weight": 0.7, "max_weight": 0.6}
            )


class TestOptimizationResults:
    """Tests for OptimizationResults domain model."""
    
    def test_valid_results(self):
        """Test creating valid optimization results."""
        results = OptimizationResults(
            optimal_weights=[0.4, 0.35, 0.25],
            expected_return=0.08,
            volatility=0.12,
            sharpe_ratio=1.5
        )
        
        assert len(results.optimal_weights) == 3
        assert abs(sum(results.optimal_weights) - 1.0) < 0.01  # Should sum to 1
    
    def test_weights_sum_validation(self):
        """Test that optimal weights must sum to 1.0."""
        with pytest.raises(ValidationError):
            OptimizationResults(
                optimal_weights=[0.4, 0.4, 0.4],  # Sum = 1.2
                expected_return=0.08,
                volatility=0.12,
                sharpe_ratio=1.5
            )


class TestRebalancingRecommendation:
    """Tests for RebalancingRecommendation domain model."""
    
    def test_valid_recommendation(self):
        """Test creating valid rebalancing recommendation."""
        dates = [
            datetime(2023, 3, 15),
            datetime(2023, 9, 20),
            datetime(2024, 2, 10)
        ]
        drifts = [0.12, 0.15, 0.11]
        
        rec = RebalancingRecommendation(
            rebalance_dates=dates,
            drift_at_rebalance=drifts,
            trigger_threshold=0.10,
            avg_drift=0.127,
            max_drift=0.15,
            cost_benefit_ratio=2.5,
            sharpe_improvement=0.08,
            total_transaction_costs=0.003,
            portfolio_value_at_dates=[100000, 105000, 110000]
        )
        
        assert len(rec.rebalance_dates) == 3
        assert rec.avg_drift == 0.127
        assert rec.max_drift == 0.15
    
    def test_dates_and_drift_same_length(self):
        """Test that dates and drift lists must have same length."""
        with pytest.raises(ValidationError):
            RebalancingRecommendation(
                rebalance_dates=[datetime(2023, 3, 15), datetime(2023, 9, 20)],
                drift_at_rebalance=[0.12],  # Wrong length
                trigger_threshold=0.10,
                avg_drift=0.12,
                max_drift=0.12,
                cost_benefit_ratio=1.5,
                sharpe_improvement=0.05,
                total_transaction_costs=0.002
            )


class TestNewsModels:
    """Tests for news and event domain models."""
    
    def test_surprise_event(self):
        """Test creating surprise event."""
        event = SurpriseEvent(
            date=datetime(2023, 10, 15),
            symbol="SPY",
            event_type=EventType.VOLATILITY_SPIKE,
            magnitude=0.35,
            description="Volatility spike detected",
            z_score=3.2,
            affected_value=35.0
        )
        
        assert event.symbol == "SPY"
        assert event.event_type == EventType.VOLATILITY_SPIKE
        assert event.z_score == 3.2
    
    def test_news_article(self):
        """Test creating news article."""
        article = NewsArticle(
            title="Market volatility increases",
            description="Stock market saw increased volatility...",
            url="https://example.com/article",
            source="Financial Times",
            published_at=datetime(2023, 10, 15),
            relevance_score=0.85
        )
        
        assert article.source == "Financial Times"
        assert 0 <= article.relevance_score <= 1
    
    def test_event_news_correlation(self):
        """Test creating event-news correlation."""
        event = SurpriseEvent(
            date=datetime(2023, 10, 15),
            event_type=EventType.PORTFOLIO_SHOCK,
            magnitude=0.05,
            description="Portfolio shock",
            z_score=2.5,
            affected_value=-5000
        )
        
        articles = [
            NewsArticle(
                title="Market drops",
                description="Markets fell today",
                url="https://example.com/1",
                source="News Corp",
                published_at=datetime(2023, 10, 15),
                relevance_score=0.9
            )
        ]
        
        correlation = EventNewsCorrelation(
            event=event,
            articles=articles,
            correlation_strength=0.75,
            key_themes=["market", "drop", "volatility"],
            ai_analysis="Strong correlation between event and news coverage"
        )
        
        assert correlation.correlation_strength == 0.75
        assert len(correlation.articles) == 1
        assert len(correlation.key_themes) == 3


class TestPortfolioModels:
    """Tests for portfolio domain models."""
    
    def test_instrument_domain_model(self):
        """Test creating instrument domain model."""
        instrument = InstrumentDomainModel(
            symbol="spy",  # Should be uppercased
            name="SPDR S&P 500 ETF",
            instrument_type=InstrumentType.ETF,
            sector="Broad Market",
            currency="usd",  # Should be uppercased
            quantity=100,
            current_value_local=45000,
            current_value_base=45000,
            weight_pct=45.0
        )
        
        assert instrument.symbol == "SPY"  # Uppercased
        assert instrument.currency == "USD"  # Uppercased
        assert instrument.instrument_type == InstrumentType.ETF
    
    def test_order_record(self):
        """Test creating order record."""
        order = OrderRecord(
            symbol="aapl",
            order_type=OrderType.BUY,
            volume=50,
            order_date=datetime(2023, 10, 1),
            price=175.50,
            notes="Initial purchase"
        )
        
        assert order.symbol == "AAPL"  # Uppercased
        assert order.order_type == OrderType.BUY
        assert order.volume == 50
    
    def test_order_zero_volume_rejected(self):
        """Test that zero volume orders are rejected."""
        with pytest.raises(ValidationError):
            OrderRecord(
                symbol="AAPL",
                order_type=OrderType.BUY,
                volume=0,  # Invalid
                order_date=datetime(2023, 10, 1)
            )
    
    def test_price_history(self):
        """Test creating price history."""
        history = PriceHistory(
            symbol="spy",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 12, 31),
            prices={
                'date': [datetime(2023, 1, 1), datetime(2023, 1, 2)],
                'open': [400.0, 405.0],
                'high': [410.0, 415.0],
                'low': [395.0, 400.0],
                'close': [405.0, 410.0],
                'volume': [1000000, 1100000]
            },
            dividends=[
                {'ex_date': datetime(2023, 3, 15), 'amount': 1.50},
                {'ex_date': datetime(2023, 6, 15), 'amount': 1.60}
            ]
        )
        
        assert history.symbol == "SPY"
        assert len(history.dividends) == 2
        assert 'close' in history.prices
    
    def test_price_history_end_after_start(self):
        """Test that end_date must be after start_date."""
        with pytest.raises(ValidationError):
            PriceHistory(
                symbol="SPY",
                start_date=datetime(2023, 12, 31),
                end_date=datetime(2023, 1, 1),  # Before start
                prices={
                    'date': [datetime(2023, 1, 1)],
                    'open': [400.0],
                    'high': [410.0],
                    'low': [395.0],
                    'close': [405.0],
                    'volume': [1000000]
                }
            )
    
    def test_price_history_missing_keys(self):
        """Test that prices dict must have all required keys."""
        with pytest.raises(ValidationError):
            PriceHistory(
                symbol="SPY",
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 12, 31),
                prices={
                    'date': [datetime(2023, 1, 1)],
                    'close': [405.0]
                    # Missing open, high, low, volume
                }
            )
    
    def test_portfolio_summary(self):
        """Test creating portfolio summary."""
        holdings = [
            InstrumentDomainModel(
                symbol="SPY",
                name="SPDR S&P 500",
                instrument_type=InstrumentType.ETF,
                quantity=100,
                current_value_local=45000,
                current_value_base=45000,
                weight_pct=60.0
            ),
            InstrumentDomainModel(
                symbol="AGG",
                name="iShares Core US Aggregate Bond",
                instrument_type=InstrumentType.ETF,
                quantity=200,
                current_value_local=30000,
                current_value_base=30000,
                weight_pct=40.0
            )
        ]
        
        summary = PortfolioSummary(
            total_value=75000,
            base_currency="USD",
            holdings=holdings,
            sharpe=1.2,
            volatility=0.12,
            max_drawdown=-0.15
        )
        
        assert summary.total_value == 75000
        assert len(summary.holdings) == 2
        assert summary.sharpe == 1.2
    
    def test_portfolio_weights_must_sum_to_100(self):
        """Test that holdings weights must sum to ~100%."""
        holdings = [
            InstrumentDomainModel(
                symbol="SPY",
                name="SPDR S&P 500",
                instrument_type=InstrumentType.ETF,
                quantity=100,
                current_value_local=45000,
                current_value_base=45000,
                weight_pct=50.0  # Total = 90%, invalid
            ),
            InstrumentDomainModel(
                symbol="AGG",
                name="iShares Core US Aggregate Bond",
                instrument_type=InstrumentType.ETF,
                quantity=200,
                current_value_local=30000,
                current_value_base=30000,
                weight_pct=40.0
            )
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            PortfolioSummary(
                total_value=75000,
                base_currency="USD",
                holdings=holdings
            )
        
        assert "sum to ~100%" in str(exc_info.value)
    
    def test_portfolio_total_value_matches_holdings(self):
        """Test that total_value must match sum of holdings."""
        holdings = [
            InstrumentDomainModel(
                symbol="SPY",
                name="SPDR S&P 500",
                instrument_type=InstrumentType.ETF,
                quantity=100,
                current_value_local=45000,
                current_value_base=45000,
                weight_pct=60.0
            ),
            InstrumentDomainModel(
                symbol="AGG",
                name="iShares Core US Aggregate Bond",
                instrument_type=InstrumentType.ETF,
                quantity=200,
                current_value_local=30000,
                current_value_base=30000,
                weight_pct=40.0
            )
        ]
        
        # Holdings sum to 75000, but total_value is 100000
        with pytest.raises(ValidationError) as exc_info:
            PortfolioSummary(
                total_value=100000,  # Doesn't match holdings
                base_currency="USD",
                holdings=holdings
            )
        
        assert "doesn't match sum of holdings" in str(exc_info.value)


class TestDomainModelSerialization:
    """Tests for domain model JSON serialization."""
    
    def test_simulation_parameters_round_trip(self):
        """Test SimulationParameters JSON round-trip."""
        params = SimulationParameters(
            symbols=["SPY", "AGG"],
            weights=[0.6, 0.4],
            years=10,
            num_simulations=1000,
            initial_value=100000
        )
        
        json_str = params.to_json()
        restored = SimulationParameters.from_json(json_str)
        
        assert restored.symbols == params.symbols
        assert restored.weights == params.weights
        assert restored.years == params.years
    
    def test_portfolio_summary_round_trip(self):
        """Test PortfolioSummary JSON round-trip."""
        holdings = [
            InstrumentDomainModel(
                symbol="SPY",
                name="SPDR S&P 500",
                instrument_type=InstrumentType.ETF,
                quantity=100,
                current_value_local=45000,
                current_value_base=45000,
                weight_pct=100.0
            )
        ]
        
        summary = PortfolioSummary(
            total_value=45000,
            base_currency="USD",
            holdings=holdings,
            sharpe=1.5
        )
        
        json_str = summary.to_json()
        restored = PortfolioSummary.from_json(json_str)
        
        assert restored.total_value == summary.total_value
        assert len(restored.holdings) == 1
        assert restored.holdings[0].symbol == "SPY"
        assert restored.sharpe == 1.5
