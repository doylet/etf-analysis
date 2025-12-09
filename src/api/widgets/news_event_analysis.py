"""News Event Analysis Widget API Adapter."""

from typing import Dict, Any
import logging

from src.api.widgets.base import BaseWidgetAdapter
from src.api.widgets.exceptions import WidgetValidationError
from src.widgets.news_event_analysis_widget import NewsEventAnalysisWidget

logger = logging.getLogger(__name__)


class NewsEventAnalysisAdapter(BaseWidgetAdapter):
    """Adapter to expose news event analysis widget through API."""
    
    def __init__(self, storage):
        super().__init__(storage, NewsEventAnalysisWidget)
        
    def get_widget_name(self) -> str:
        return "news_event_analysis"
        
    def get_widget_description(self) -> str:
        return "Analyze impact of news and events on portfolio"
        
    def validate_input_parameters(self, **kwargs) -> Dict[str, Any]:
        validated = {}
        portfolio_id = kwargs.get('portfolio_id')
        if portfolio_id is not None:
            if not isinstance(portfolio_id, str) or not portfolio_id.strip():
                raise WidgetValidationError("portfolio_id must be a non-empty string")
            validated['portfolio_id'] = portfolio_id.strip()
        else:
            validated['portfolio_id'] = None
        
        # Validate lookback_days
        lookback_days = kwargs.get('lookback_days', 30)
        valid_lookbacks = [7, 14, 30, 60, 90]
        if lookback_days not in valid_lookbacks:
            raise WidgetValidationError(f"lookback_days must be one of {valid_lookbacks}")
        validated['lookback_days'] = lookback_days
        
        # Validate surprise_threshold
        surprise_threshold = kwargs.get('surprise_threshold', 5.0)
        try:
            surprise_threshold = float(surprise_threshold)
            if surprise_threshold < 1 or surprise_threshold > 20:
                raise WidgetValidationError("surprise_threshold must be between 1 and 20")
            validated['surprise_threshold'] = surprise_threshold
        except (TypeError, ValueError):
            raise WidgetValidationError("surprise_threshold must be a number")
        
        return validated
        
    def extract_calculation_data(self, widget_instance, validated_params: Dict[str, Any] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        import random
        
        if validated_params is None:
            validated_params = {}
        
        lookback_days = validated_params.get('lookback_days', 30)
        surprise_threshold = validated_params.get('surprise_threshold', 5.0)
        
        try:
            instruments = self.storage.get_all_instruments()
            if not instruments:
                return {"message": "No instruments available"}
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            if not holdings:
                return {"message": "No active holdings"}
            
            # Generate sample sentiment analysis
            # In a full implementation, this would fetch and analyze actual news
            symbols = [h['symbol'] for h in holdings]
            
            # Sample sentiment scores
            sentiments = [random.uniform(-1, 1) for _ in symbols]
            overall_sentiment = sum(sentiments) / len(sentiments)
            
            # Sample market impact correlation
            price_correlation = random.uniform(0.3, 0.8)
            
            # Sample recent events
            events = []
            for i, symbol in enumerate(symbols[:3]):
                events.append({
                    "title": f"Market Update: {symbol}",
                    "date": (datetime.now() - timedelta(days=i*7)).isoformat(),
                    "sentiment": float(sentiments[i]),
                    "source": "Market Data"
                })
            
            return {
                "sentiment_analysis": {
                    "overall_sentiment": float(overall_sentiment),
                    "positive_count": len([s for s in sentiments if s > 0]),
                    "negative_count": len([s for s in sentiments if s < 0]),
                    "neutral_count": len([s for s in sentiments if s == 0])
                },
                "market_impact": {
                    "price_correlation": float(price_correlation),
                    "volatility_impact": float(random.uniform(0.1, 0.5))
                },
                "events": events,
                "holdings_analyzed": len(symbols)
            }
        except Exception as e:
            logger.error(f"News analysis extraction failed: {e}")
            return {"error": str(e)}
