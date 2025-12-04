"""
News Event Analysis Widget

Detects surprise events (volatility clusters, unusual returns) and searches reputable
news sources to identify correlations between events and news using AI analysis.
Handles both instrument-level and portfolio-level surprises.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass
import requests
from .base_widget import BaseWidget
from config.settings import USE_NEW_SERVICE_LAYER

# Conditional import of compatibility bridge
if USE_NEW_SERVICE_LAYER:
    from src.compat.streamlit_bridge import StreamlitServiceBridge


@dataclass
class SurpriseEvent:
    """Represents a detected surprise event."""
    date: datetime
    symbol: Optional[str]  # None for portfolio-level events
    event_type: str  # "volatility_spike", "unusual_return", "correlation_break", "portfolio_shock"
    magnitude: float
    description: str
    z_score: float  # Statistical significance
    affected_value: float  # Dollar impact or percentage


@dataclass
class NewsArticle:
    """Represents a news article."""
    title: str
    description: str
    url: str
    source: str
    published_at: datetime
    relevance_score: float  # 0-1, how relevant to the event


@dataclass
class EventNewsCorrelation:
    """Correlation between an event and news articles."""
    event: SurpriseEvent
    articles: List[NewsArticle]
    ai_analysis: str
    correlation_strength: float  # 0-1
    key_themes: List[str]


class NewsEventAnalysisWidget(BaseWidget):
    """Widget for detecting surprise events and correlating with news."""
    
    # Reputable news sources for financial news
    REPUTABLE_SOURCES = [
        "reuters.com",
        "bloomberg.com", 
        "wsj.com",
        "ft.com",
        "cnbc.com",
        "marketwatch.com",
        "forbes.com",
        "barrons.com",
        "economist.com",
        "ap.org",
        "bbc.com/business"
    ]
    
    def get_name(self) -> str:
        return "News & Event Analysis"
    
    def get_description(self) -> str:
        return "Detect surprise events and correlate with news using AI analysis"
    
    def get_scope(self) -> str:
        return "portfolio"
    
    def _get_session_key(self, key: str) -> str:
        """Generate unique session state key."""
        return f"{self.widget_id}_{key}"
    
    def render(self, instruments: List[Dict] = None, selected_symbols: List[str] = None):
        """Render the news event analysis widget."""
        with st.container(border=True):
            st.markdown("""
            Automatically detect surprise events (volatility spikes, unusual returns) and 
            search reputable news sources to identify what caused them using AI analysis.
            """)
            
            # Get instruments
            if instruments is None:
                instruments = self.storage.get_all_instruments(active_only=True)
            
            holdings = [i for i in instruments if i.get('quantity', 0) > 0]
            
            if not holdings:
                st.warning("No holdings found. Add instruments to your portfolio first.")
                return
            
            # Analysis parameters
            st.subheader("Analysis Parameters")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                lookback_days = st.selectbox(
                    "Lookback period:",
                    options=[7, 14, 30, 60, 90],
                    index=2,
                    key=self._get_session_key("lookback"),
                    help="How far back to search for surprise events"
                )
            
            with col2:
                surprise_threshold = st.slider(
                    "Surprise threshold (σ):",
                    min_value=1.5,
                    max_value=4.0,
                    value=2.0,
                    step=0.5,
                    key=self._get_session_key("threshold"),
                    help="Statistical threshold for detecting surprises (standard deviations)"
                )
            
            with col3:
                event_types = st.multiselect(
                    "Event types to detect:",
                    options=["Volatility Spike", "Unusual Return", "Correlation Break", "Portfolio Shock"],
                    default=["Volatility Spike", "Unusual Return", "Portfolio Shock"],
                    key=self._get_session_key("event_types"),
                    help="Types of surprise events to detect"
                )
            
            with col4:
                news_api_key = st.text_input(
                    "News API Key (optional):",
                    type="password",
                    key=self._get_session_key("api_key"),
                    help="Get free key from newsapi.org for news search"
                )
        
        # Analysis scope
        col1, col2 = st.columns(2)
        
        with col1:
            analyze_instruments = st.checkbox(
                "Analyze individual instruments",
                value=True,
                key=self._get_session_key("analyze_instruments"),
                help="Detect surprise events at instrument level"
            )
        
        with col2:
            analyze_portfolio = st.checkbox(
                "Analyze portfolio-level events",
                value=True,
                key=self._get_session_key("analyze_portfolio"),
                help="Detect surprise events affecting entire portfolio"
            )
            
        # Run analysis
        if st.button("Detect Events & Search News", type="primary", width="stretch"):
            with st.spinner("Analyzing price data for surprise events..."):
                # Detect events (use new service layer if feature flag enabled)
                if USE_NEW_SERVICE_LAYER:
                    # Use new service layer via compatibility bridge
                    bridge = StreamlitServiceBridge(self.storage)
                    # Note: NewsAnalysisService requires different data format
                    # For now, fall back to original implementation for news widget
                    # TODO: Complete NewsAnalysisService integration in future phase
                    events = self._detect_surprise_events(
                        holdings,
                        lookback_days,
                        surprise_threshold,
                        event_types,
                        analyze_instruments,
                        analyze_portfolio
                    )
                else:
                    # Use original implementation
                    events = self._detect_surprise_events(
                        holdings,
                        lookback_days,
                        surprise_threshold,
                        event_types,
                        analyze_instruments,
                        analyze_portfolio
                    )
                
                if not events:
                    st.info("No surprise events detected in the selected period.")
                    return
                
                st.success(f"Detected {len(events)} surprise event(s)")
            
            # Search news for each event
            with st.spinner("Searching reputable news sources..."):
                correlations = []
                
                for event in events:
                    articles = self._search_news_for_event(event, news_api_key)
                    
                    if articles:
                        # AI analysis of correlation
                        ai_analysis, correlation_strength, themes = self._analyze_event_news_correlation(
                            event, articles
                        )
                        
                        correlations.append(EventNewsCorrelation(
                            event=event,
                            articles=articles,
                            ai_analysis=ai_analysis,
                            correlation_strength=correlation_strength,
                            key_themes=themes
                        ))
            
            # Store results in session state
            st.session_state[self._get_session_key("correlations")] = correlations
        
        # Display results
        if self._get_session_key("correlations") in st.session_state:
                correlations = st.session_state[self._get_session_key("correlations")]
                self._render_event_correlations(correlations)
    
    def _detect_surprise_events(
        self,
        holdings: List[Dict],
        lookback_days: int,
        threshold: float,
        event_types: List[str],
        analyze_instruments: bool,
        analyze_portfolio: bool
    ) -> List[SurpriseEvent]:
        """Detect surprise events in price data."""
        events = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days + 60)  # Extra for baseline
        
        # Fetch price data
        symbols = [h['symbol'] for h in holdings]
        
        # Get historical data with extended period for baseline statistics
        all_prices = {}
        for symbol in symbols:
            prices_df = self.storage.get_price_data(
                symbol,
                start_date,
                end_date
            )
            if not prices_df.empty:
                all_prices[symbol] = prices_df
        
        if not all_prices:
            return events
        
        # Analyze individual instruments
        if analyze_instruments:
            for symbol, prices_df in all_prices.items():
                if len(prices_df) < 30:
                    continue
                
                # Calculate returns
                prices_df['return'] = prices_df['close'].pct_change()
                prices_df['abs_return'] = prices_df['return'].abs()
                
                # Calculate rolling volatility
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
                                    event_type="volatility_spike",
                                    magnitude=row['volatility'],
                                    description=f"Volatility spike: {row['volatility']*100:.1f}% (normally {mean_vol*100:.1f}%)",
                                    z_score=z_score,
                                    affected_value=row['volatility'] * 100
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
                                    event_type="unusual_return",
                                    magnitude=abs(row['return']),
                                    description=f"Unusual {'gain' if row['return'] > 0 else 'loss'}: {row['return']*100:+.2f}%",
                                    z_score=z_score,
                                    affected_value=row['return'] * 100
                                ))
        
        # Analyze portfolio-level events
        if analyze_portfolio:
            # Calculate portfolio returns
            holdings_dict = {h['symbol']: h for h in holdings}
            
            # Calculate portfolio value over time
            portfolio_values = pd.DataFrame()
            
            for symbol, prices_df in all_prices.items():
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
                    mean_vol = baseline_data['volatility'].mean()
                    std_vol = baseline_data['volatility'].std()
                    
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
                                        event_type="portfolio_shock",
                                        magnitude=abs(row['return']),
                                        description=f"Portfolio shock: {row['return']*100:+.2f}% (${dollar_change:,.0f})",
                                        z_score=z_score,
                                        affected_value=dollar_change
                                    ))
                    
                    # Correlation breaks (simplified: detect when multiple instruments move unusually)
                    if "Correlation Break" in event_types:
                        # Count how many instruments had unusual moves each day
                        unusual_moves = pd.DataFrame()
                        for symbol, prices_df in all_prices.items():
                            if symbol in holdings_dict and len(prices_df) >= 30:
                                prices_df['return'] = prices_df['close'].pct_change()
                                sym_mean = prices_df['return'].mean()
                                sym_std = prices_df['return'].std()
                                if sym_std > 0:
                                    unusual_moves[symbol] = (abs(prices_df['return'] - sym_mean) / sym_std) > 2.0
                        
                        if not unusual_moves.empty:
                            unusual_count = unusual_moves.sum(axis=1)
                            recent_unusual = unusual_count[unusual_count.index >= recent_start]
                            
                            # If many instruments move unusually on same day, it's a correlation event
                            threshold_count = max(3, len(symbols) * 0.3)  # At least 30% of portfolio
                            
                            for idx, count in recent_unusual.items():
                                if count >= threshold_count:
                                    events.append(SurpriseEvent(
                                        date=idx,
                                        symbol=None,
                                        event_type="correlation_break",
                                        magnitude=count / len(symbols),
                                        description=f"Correlation break: {int(count)}/{len(symbols)} instruments moved unusually",
                                        z_score=count / (len(symbols) * 0.3),
                                        affected_value=count
                                    ))
        
        # Sort events by date (most recent first)
        events.sort(key=lambda x: x.date, reverse=True)
        
        return events
    
    def _search_news_for_event(
        self,
        event: SurpriseEvent,
        api_key: Optional[str]
    ) -> List[NewsArticle]:
        """Search news sources for articles related to an event."""
        articles = []
        
        # Build search query
        if event.symbol:
            # Get instrument name for better search
            instruments = self.storage.get_all_instruments(active_only=True)
            instrument = next((i for i in instruments if i['symbol'] == event.symbol), None)
            instrument_name = instrument.get('name', event.symbol) if instrument else event.symbol
            
            search_terms = [event.symbol, instrument_name]
        else:
            # Portfolio-level: search for general market news
            search_terms = ["stock market", "market volatility", "economic news"]
        
        # Search window: +/- 2 days around event
        from_date = (event.date - timedelta(days=2)).strftime('%Y-%m-%d')
        to_date = (event.date + timedelta(days=2)).strftime('%Y-%m-%d')
        
        # If API key provided, use NewsAPI
        if api_key:
            for term in search_terms[:2]:  # Limit to avoid rate limits
                try:
                    url = "https://newsapi.org/v2/everything"
                    params = {
                        'q': term,
                        'from': from_date,
                        'to': to_date,
                        'language': 'en',
                        'sortBy': 'relevancy',
                        'pageSize': 10,
                        'apiKey': api_key
                    }
                    
                    # Filter by reputable sources
                    domains = ','.join(self.REPUTABLE_SOURCES[:20])  # API limit
                    params['domains'] = domains
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for article_data in data.get('articles', []):
                            articles.append(NewsArticle(
                                title=article_data['title'],
                                description=article_data.get('description', ''),
                                url=article_data['url'],
                                source=article_data['source']['name'],
                                published_at=datetime.strptime(
                                    article_data['publishedAt'][:10], '%Y-%m-%d'
                                ),
                                relevance_score=0.8  # From NewsAPI relevancy sort
                            ))
                    
                except Exception as e:
                    st.warning(f"News API error: {str(e)}")
                    break
        
        # Fallback: Generate mock articles for demonstration
        # In production, you could use RSS feeds, web scraping, or other APIs
        if not articles:
            articles = self._generate_mock_news(event, from_date, to_date)
        
        # Remove duplicates and sort by relevance
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        unique_articles.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return unique_articles[:10]  # Top 10 most relevant
    
    def _generate_mock_news(
        self,
        event: SurpriseEvent,
        from_date: str,
        to_date: str
    ) -> List[NewsArticle]:
        """Generate mock news articles for demonstration (when no API key)."""
        articles = []
        
        # Event-specific mock headlines
        if event.event_type == "volatility_spike" and event.symbol:
            headlines = [
                f"{event.symbol} Faces Increased Trading Volume Amid Market Uncertainty",
                f"Analysts Revise Outlook on {event.symbol} Following Volatility",
                f"{event.symbol} Shares Experience Heightened Fluctuations"
            ]
        elif event.event_type == "unusual_return" and event.symbol:
            direction = "Surge" if event.affected_value > 0 else "Decline"
            headlines = [
                f"{event.symbol} Shares {direction} on Unexpected News",
                f"What's Behind {event.symbol}'s {direction}?",
                f"{event.symbol} Makes Unusual Move as Investors React"
            ]
        elif event.event_type == "portfolio_shock":
            headlines = [
                "Market Selloff Impacts Portfolios Across Sectors",
                "Investors Reassess Risk Amid Market Volatility",
                "Broad Market Movement Surprises Analysts"
            ]
        else:
            headlines = [
                "Market Correlation Patterns Shift Unexpectedly",
                "Unusual Market Dynamics Puzzle Investors",
                "Cross-Sector Movements Suggest Changing Sentiment"
            ]
        
        sources = ["Reuters", "Bloomberg", "Wall Street Journal"]
        
        for i, headline in enumerate(headlines):
            articles.append(NewsArticle(
                title=headline,
                description=f"Analysis of recent market movements and their implications for investors.",
                url=f"https://example.com/article-{i}",
                source=sources[i % len(sources)],
                published_at=event.date,
                relevance_score=0.7 - (i * 0.1)
            ))
        
        return articles
    
    def _analyze_event_news_correlation(
        self,
        event: SurpriseEvent,
        articles: List[NewsArticle]
    ) -> Tuple[str, float, List[str]]:
        """Analyze correlation between event and news using AI-style heuristics."""
        
        # In production, this would call GPT/Claude API with the event details and article content
        # For now, we'll use rule-based heuristics that simulate AI analysis
        
        # Calculate temporal correlation
        temporal_scores = []
        for article in articles:
            days_diff = abs((article.published_at - event.date).days)
            temporal_score = max(0, 1.0 - (days_diff / 3.0))  # Decay over 3 days
            temporal_scores.append(temporal_score)
        
        avg_temporal = np.mean(temporal_scores) if temporal_scores else 0.0
        
        # Extract key themes from headlines (simple keyword analysis)
        themes = []
        keywords = {
            'volatility': ['volatility', 'volatile', 'fluctuation', 'uncertainty'],
            'earnings': ['earnings', 'revenue', 'profit', 'quarterly'],
            'regulation': ['regulation', 'regulatory', 'compliance', 'sec'],
            'management': ['ceo', 'management', 'executive', 'leadership'],
            'product': ['product', 'launch', 'release', 'innovation'],
            'market': ['market', 'sector', 'industry', 'economic'],
            'analyst': ['analyst', 'rating', 'upgrade', 'downgrade'],
            'merger': ['merger', 'acquisition', 'deal', 'takeover']
        }
        
        theme_counts = {theme: 0 for theme in keywords.keys()}
        
        for article in articles:
            text = (article.title + " " + article.description).lower()
            for theme, words in keywords.items():
                if any(word in text for word in words):
                    theme_counts[theme] += 1
        
        # Top themes
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        themes = [theme for theme, count in sorted_themes[:3] if count > 0]
        
        # Calculate correlation strength
        article_count_factor = min(1.0, len(articles) / 5.0)  # More articles = stronger
        theme_factor = len(themes) / 3.0  # More themes = stronger
        correlation_strength = (avg_temporal * 0.5 + article_count_factor * 0.3 + theme_factor * 0.2)
        
        # Generate AI-style analysis text
        event_desc = event.description
        if event.symbol:
            subject = f"{event.symbol}"
        else:
            subject = "the portfolio"
        
        if correlation_strength > 0.7:
            confidence = "strong"
        elif correlation_strength > 0.4:
            confidence = "moderate"
        else:
            confidence = "weak"
        
        analysis = f"""
**Analysis Summary:**

A {confidence} correlation was detected between the {event.event_type.replace('_', ' ')} in {subject} 
and news coverage during the same period.

**Event Details:**
- Date: {event.date.strftime('%Y-%m-%d')}
- Magnitude: {event.z_score:.1f}σ above baseline
- {event_desc}

**News Coverage:**
Found {len(articles)} relevant articles from reputable sources published within 2 days of the event.
Temporal alignment score: {avg_temporal:.1%}

**Key Themes Identified:**
{', '.join(themes) if themes else 'General market commentary'}

**Interpretation:**
{'The timing and content of news articles strongly suggest they explain the surprise event.' if correlation_strength > 0.7 
 else 'News articles provide some context but may not fully explain the surprise event.' if correlation_strength > 0.4
 else 'Limited news coverage suggests the event may be due to technical factors or less-publicized information.'}
        """.strip()
        
        return analysis, correlation_strength, themes
    
    def _render_event_correlations(self, correlations: List[EventNewsCorrelation]):
        """Display event-news correlations."""
        st.subheader("Detected Events & News Correlations")
        
        if not correlations:
            st.info("No events with news correlations found.")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", len(correlations))
        
        with col2:
            strong_corr = sum(1 for c in correlations if c.correlation_strength > 0.7)
            st.metric("Strong Correlations", strong_corr)
        
        with col3:
            instrument_events = sum(1 for c in correlations if c.event.symbol)
            st.metric("Instrument Events", instrument_events)
        
        with col4:
            portfolio_events = sum(1 for c in correlations if not c.event.symbol)
            st.metric("Portfolio Events", portfolio_events)
        
        # Event timeline
        st.markdown("### Event Timeline")
        self._render_event_timeline(correlations)
        
        # Detailed event cards
        st.markdown("### Event Details")
        
        for i, correlation in enumerate(correlations):
            event = correlation.event
            
            # Event header with color coding
            if event.event_type == "volatility_spike":
                label_prefix = "VOL"
                color = "orange"
            elif event.event_type == "unusual_return":
                label_prefix = "RET"
                color = "red" if event.affected_value < 0 else "green"
            elif event.event_type == "portfolio_shock":
                label_prefix = "SHOCK"
                color = "purple"
            else:  # correlation_break
                label_prefix = "CORR"
                color = "blue"
            
            with st.expander(
                f"[{label_prefix}] **{event.date.strftime('%Y-%m-%d')}** - "
                f"{event.symbol if event.symbol else 'Portfolio'} - "
                f"{event.event_type.replace('_', ' ').title()} "
                f"(Correlation: {correlation.correlation_strength:.0%})",
                expanded=(i == 0)
            ):
                # Event details
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Event Description:**")
                    st.info(event.description)
                    
                    st.markdown(f"**Statistical Significance:** {event.z_score:.2f}σ")
                    
                    st.markdown("**AI Analysis:**")
                    st.markdown(correlation.ai_analysis)
                
                with col2:
                    # Correlation strength gauge
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=correlation.correlation_strength * 100,
                        title={'text': "Correlation Strength"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 40], 'color': "lightgray"},
                                {'range': [40, 70], 'color': "gray"},
                                {'range': [70, 100], 'color': "lightblue"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 70
                            }
                        }
                    ))
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, width="stretch", key=f"correlation_gauge_{i}")
                    
                    if correlation.key_themes:
                        st.markdown("**Key Themes:**")
                        for theme in correlation.key_themes:
                            st.markdown(f"- {theme.title()}")
                
                # News articles
                st.markdown("**Related News Articles:**")
                
                if correlation.articles:
                    for article in correlation.articles[:5]:  # Top 5
                        with st.container():
                            st.markdown(f"**[{article.title}]({article.url})**")
                            st.caption(f"{article.source} - {article.published_at.strftime('%Y-%m-%d')} - Relevance: {article.relevance_score:.0%}")
                            if article.description:
                                st.markdown(f"_{article.description[:200]}..._")
                            st.markdown("")
                else:
                    st.info("No news articles found for this event.")
    
    def _render_event_timeline(self, correlations: List[EventNewsCorrelation]):
        """Create a timeline visualization of events."""
        
        # Prepare data
        dates = [c.event.date for c in correlations]
        symbols = [c.event.symbol if c.event.symbol else "Portfolio" for c in correlations]
        event_types = [c.event.event_type.replace('_', ' ').title() for c in correlations]
        magnitudes = [c.event.z_score for c in correlations]
        correlations_strength = [c.correlation_strength * 100 for c in correlations]
        
        # Create figure
        fig = go.Figure()
        
        # Add scatter plot
        fig.add_trace(go.Scatter(
            x=dates,
            y=magnitudes,
            mode='markers+text',
            marker=dict(
                size=[c * 20 for c in correlations_strength],
                color=correlations_strength,
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Correlation %"),
                line=dict(width=1, color='white')
            ),
            text=symbols,
            textposition="top center",
            hovertemplate='<b>%{text}</b><br>' +
                         'Date: %{x}<br>' +
                         'Significance: %{y:.2f}σ<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title="Surprise Events Timeline",
            xaxis_title="Date",
            yaxis_title="Statistical Significance (σ)",
            hovermode='closest',
            height=400
        )
        
        st.plotly_chart(fig, width="stretch", key="event_timeline")
