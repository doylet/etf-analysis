"""
News and event analysis service - detects surprise events and correlates with news.

Extracted from src/widgets/news_event_analysis_widget.py to be framework-agnostic.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from domain.news import SurpriseEvent, NewsArticle, EventNewsCorrelation, EventType


class NewsAnalysisService:
    """Service for detecting surprise events and analyzing news correlations."""
    
    @staticmethod
    def detect_surprise_events(
        prices_data: Dict[str, pd.DataFrame],
        lookback_days: int,
        threshold: float = 2.0,
        event_types: Optional[List[str]] = None,
        analyze_instruments: bool = True,
        analyze_portfolio: bool = True,
        holdings: Optional[List[Dict]] = None
    ) -> List[SurpriseEvent]:
        """
        Detect surprise events in price data using statistical thresholds.
        
        Args:
            prices_data: Dict of {symbol: price_df} with OHLCV data
            lookback_days: Days to analyze for events
            threshold: Z-score threshold for event detection (default 2.0)
            event_types: List of event types to detect (default: all)
            analyze_instruments: Whether to analyze individual instruments
            analyze_portfolio: Whether to analyze portfolio-level events
            holdings: List of holdings dicts with 'symbol' and 'quantity' (for portfolio analysis)
            
        Returns:
            List of detected SurpriseEvents sorted by date (most recent first)
        """
        if event_types is None:
            event_types = ["Volatility Spike", "Unusual Return", "Portfolio Shock", "Correlation Break"]
        
        events = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days + 60)  # Extra for baseline
        
        if not prices_data:
            return events
        
        # Analyze individual instruments
        if analyze_instruments:
            for symbol, prices_df in prices_data.items():
                if len(prices_df) < 30:
                    continue
                
                # Calculate returns and volatility
                prices_df = prices_df.copy()
                prices_df['return'] = prices_df['close'].pct_change()
                prices_df['volatility'] = prices_df['return'].rolling(window=20).std()
                
                # Baseline statistics (first 60 days)
                baseline_end = start_date + timedelta(days=60)
                baseline_data = prices_df[prices_df.index < baseline_end]
                
                if len(baseline_data) < 30:
                    continue
                
                mean_return = baseline_data['return'].mean()
                std_return = baseline_data['return'].std()
                mean_vol = baseline_data['volatility'].mean()
                std_vol = baseline_data['volatility'].std()
                
                # Focus on recent period
                recent_start = end_date - timedelta(days=lookback_days)
                recent_data = prices_df[prices_df.index >= recent_start]
                
                # Detect volatility spikes
                if "Volatility Spike" in event_types and std_vol > 0:
                    for idx, row in recent_data.iterrows():
                        if pd.notna(row['volatility']):
                            z_score = (row['volatility'] - mean_vol) / std_vol
                            if z_score > threshold:
                                events.append(SurpriseEvent(
                                    date=idx,
                                    symbol=symbol,
                                    event_type=EventType.VOLATILITY_SPIKE,
                                    magnitude=float(row['volatility']),
                                    description=f"Volatility spike: {row['volatility']*100:.1f}% (normally {mean_vol*100:.1f}%)",
                                    z_score=float(z_score),
                                    affected_value=float(row['volatility'] * 100)
                                ))
                
                # Detect unusual returns
                if "Unusual Return" in event_types and std_return > 0:
                    for idx, row in recent_data.iterrows():
                        if pd.notna(row['return']):
                            z_score = abs(row['return'] - mean_return) / std_return
                            if z_score > threshold:
                                events.append(SurpriseEvent(
                                    date=idx,
                                    symbol=symbol,
                                    event_type=EventType.UNUSUAL_RETURN,
                                    magnitude=float(abs(row['return'])),
                                    description=f"Unusual {'gain' if row['return'] > 0 else 'loss'}: {row['return']*100:+.2f}%",
                                    z_score=float(z_score),
                                    affected_value=float(row['return'] * 100)
                                ))
        
        # Analyze portfolio-level events
        if analyze_portfolio and holdings:
            holdings_dict = {h['symbol']: h for h in holdings}
            
            # Calculate portfolio value over time
            portfolio_values = pd.DataFrame()
            
            for symbol, prices_df in prices_data.items():
                if symbol in holdings_dict:
                    quantity = holdings_dict[symbol].get('quantity', 0)
                    portfolio_values[symbol] = prices_df['close'] * quantity
            
            if not portfolio_values.empty:
                portfolio_values['total'] = portfolio_values.sum(axis=1)
                portfolio_values['return'] = portfolio_values['total'].pct_change()
                portfolio_values['volatility'] = portfolio_values['return'].rolling(window=20).std()
                
                # Baseline statistics
                baseline_end = start_date + timedelta(days=60)
                baseline_data = portfolio_values[portfolio_values.index < baseline_end]
                
                if len(baseline_data) >= 30:
                    mean_return = baseline_data['return'].mean()
                    std_return = baseline_data['return'].std()
                    
                    # Recent period
                    recent_start = end_date - timedelta(days=lookback_days)
                    recent_data = portfolio_values[portfolio_values.index >= recent_start]
                    
                    # Portfolio shocks
                    if "Portfolio Shock" in event_types and std_return > 0:
                        for idx, row in recent_data.iterrows():
                            if pd.notna(row['return']):
                                z_score = abs(row['return'] - mean_return) / std_return
                                if z_score > threshold:
                                    dollar_change = row['return'] * row['total']
                                    events.append(SurpriseEvent(
                                        date=idx,
                                        symbol=None,  # Portfolio-level
                                        event_type=EventType.PORTFOLIO_SHOCK,
                                        magnitude=float(abs(row['return'])),
                                        description=f"Portfolio shock: {row['return']*100:+.2f}% (${dollar_change:,.0f})",
                                        z_score=float(z_score),
                                        affected_value=float(dollar_change)
                                    ))
                    
                    # Correlation breaks
                    if "Correlation Break" in event_types:
                        symbols = list(prices_data.keys())
                        unusual_moves = pd.DataFrame()
                        
                        for symbol, prices_df in prices_data.items():
                            if symbol in holdings_dict and len(prices_df) >= 30:
                                prices_df = prices_df.copy()
                                prices_df['return'] = prices_df['close'].pct_change()
                                sym_mean = prices_df['return'].mean()
                                sym_std = prices_df['return'].std()
                                if sym_std > 0:
                                    unusual_moves[symbol] = (abs(prices_df['return'] - sym_mean) / sym_std) > 2.0
                        
                        if not unusual_moves.empty:
                            unusual_count = unusual_moves.sum(axis=1)
                            recent_unusual = unusual_count[unusual_count.index >= recent_start]
                            
                            # If many instruments move unusually on same day
                            threshold_count = max(3, len(symbols) * 0.3)
                            
                            for idx, count in recent_unusual.items():
                                if count >= threshold_count:
                                    events.append(SurpriseEvent(
                                        date=idx,
                                        symbol=None,
                                        event_type=EventType.CORRELATION_BREAK,
                                        magnitude=float(count / len(symbols)),
                                        description=f"Correlation break: {int(count)}/{len(symbols)} instruments moved unusually",
                                        z_score=float(count / (len(symbols) * 0.3)),
                                        affected_value=float(count)
                                    ))
        
        # Sort events by date (most recent first)
        events.sort(key=lambda x: x.date, reverse=True)
        
        return events
    
    @staticmethod
    def analyze_event_news_correlation(
        event: SurpriseEvent,
        articles: List[NewsArticle]
    ) -> EventNewsCorrelation:
        """
        Analyze correlation between an event and news articles.
        
        Args:
            event: Surprise event to analyze
            articles: List of news articles around the event date
            
        Returns:
            EventNewsCorrelation with analyzed correlation and themes
        """
        if not articles:
            return EventNewsCorrelation(
                event=event,
                articles=[],
                correlation_strength=0.0,
                key_themes=[],
                ai_analysis="No news articles found for this event."
            )
        
        # Calculate correlation strength based on:
        # 1. Number of articles
        # 2. Relevance scores
        # 3. Temporal proximity to event
        
        total_relevance = sum(a.relevance_score for a in articles)
        avg_relevance = total_relevance / len(articles) if articles else 0
        
        # Time proximity factor (articles closer to event date score higher)
        time_proximity = 0.0
        for article in articles:
            days_diff = abs((article.published_at - event.date).days)
            proximity_factor = max(0, 1 - (days_diff / 7))  # Decay over 7 days
            time_proximity += proximity_factor
        
        time_proximity = time_proximity / len(articles) if articles else 0
        
        # Combined correlation strength (0-1)
        num_articles_factor = min(len(articles) / 10, 1.0)  # Normalize to 10 articles
        correlation_strength = (avg_relevance * 0.4 + time_proximity * 0.3 + num_articles_factor * 0.3)
        
        # Extract key themes from article titles/descriptions
        key_themes = NewsAnalysisService._extract_themes(articles)
        
        # Generate AI analysis summary
        ai_analysis = NewsAnalysisService._generate_analysis_summary(event, articles, correlation_strength)
        
        return EventNewsCorrelation(
            event=event,
            articles=articles[:10],  # Limit to top 10 most relevant
            correlation_strength=float(correlation_strength),
            key_themes=key_themes,
            ai_analysis=ai_analysis
        )
    
    @staticmethod
    def _extract_themes(articles: List[NewsArticle]) -> List[str]:
        """Extract key themes from news articles."""
        # Simple keyword extraction (in production, use NLP/LLM)
        keywords = {}
        
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        for article in articles:
            text = (article.title + ' ' + article.description).lower()
            words = text.split()
            
            for word in words:
                word = word.strip('.,!?;:"')
                if len(word) > 4 and word not in common_words:
                    keywords[word] = keywords.get(word, 0) + 1
        
        # Return top themes
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_keywords[:5]]
    
    @staticmethod
    def _generate_analysis_summary(
        event: SurpriseEvent,
        articles: List[NewsArticle],
        correlation_strength: float
    ) -> str:
        """Generate analysis summary."""
        if correlation_strength > 0.7:
            strength_desc = "strong"
        elif correlation_strength > 0.4:
            strength_desc = "moderate"
        else:
            strength_desc = "weak"
        
        summary = f"Found {len(articles)} news article(s) with {strength_desc} correlation to the {event.event_type.value} event"
        
        if event.symbol:
            summary += f" affecting {event.symbol}"
        
        summary += f" on {event.date.strftime('%Y-%m-%d')}. "
        
        if articles:
            summary += f"Most relevant source: {articles[0].source}. "
        
        if correlation_strength > 0.6:
            summary += "News coverage suggests this event was likely driven by external factors reported in the media."
        elif correlation_strength > 0.3:
            summary += "Some news coverage found, but correlation is not definitive."
        else:
            summary += "Limited news coverage suggests this may have been a technical or idiosyncratic market movement."
        
        return summary
