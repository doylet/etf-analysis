"""
ETF Analysis Dashboard - Main Application
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from database import DatabaseManager
from data_fetcher import DataFetcher
import os

# Page configuration
st.set_page_config(
    page_title="ETF Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and data fetcher
@st.cache_resource
def init_database():
    db = DatabaseManager()
    fetcher = DataFetcher(db)
    return db, fetcher

db, fetcher = init_database()

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("📊 ETF Analysis")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Manage Instruments", "Price History", "Comparative Analysis"]
)

# ====================
# MANAGE INSTRUMENTS PAGE
# ====================
if page == "Manage Instruments":
    st.title("🔧 Manage Instruments")
    
    # Two column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add New Instrument")
        
        with st.form("add_instrument_form"):
            symbol = st.text_input("Symbol (e.g., SPY, AAPL)", key="add_symbol").upper()
            instrument_type = st.selectbox(
                "Type",
                ["etf", "stock", "index"],
                key="add_type"
            )
            sector = st.text_input("Sector (optional)", key="add_sector")
            notes = st.text_area("Notes (optional)", key="add_notes")
            
            submitted = st.form_submit_button("Add Instrument")
            
            if submitted and symbol:
                with st.spinner(f"Adding {symbol}..."):
                    result = fetcher.add_instrument(
                        symbol=symbol,
                        instrument_type=instrument_type,
                        sector=sector if sector else None,
                        notes=notes if notes else None
                    )
                    
                    if result['success']:
                        st.success(result['message'])
                        # Fetch initial price data
                        with st.spinner(f"Fetching historical data for {symbol}..."):
                            price_result = fetcher.fetch_and_store_prices(symbol, period='1y')
                            if price_result['success']:
                                st.info(f"Loaded {price_result.get('records_added', 0)} price records")
                        st.rerun()
                    else:
                        st.error(result['message'])
    
    with col2:
        st.subheader("Search Instruments")
        search_term = st.text_input("Search by symbol or name", key="search")
        
        if search_term:
            results = fetcher.search_instruments(search_term)
            if results:
                st.write(f"Found {len(results)} instrument(s):")
                for inst in results:
                    st.write(f"**{inst['symbol']}** - {inst['name']} ({inst['type']})")
            else:
                st.info("No instruments found")
    
    st.divider()
    
    # Display all tracked instruments
    st.subheader("Tracked Instruments")
    
    instruments = fetcher.get_all_instruments(active_only=True)
    
    if instruments:
        df = pd.DataFrame(instruments)
        df['added_date'] = pd.to_datetime(df['added_date']).dt.strftime('%Y-%m-%d')
        
        # Display as interactive table
        st.dataframe(
            df[['symbol', 'name', 'type', 'sector', 'added_date']],
            use_container_width=True,
            hide_index=True
        )
        
        # Remove instrument section
        st.subheader("Remove Instrument")
        col_remove1, col_remove2 = st.columns([3, 1])
        
        with col_remove1:
            remove_symbol = st.selectbox(
                "Select instrument to remove",
                options=[i['symbol'] for i in instruments],
                key="remove_select"
            )
        
        with col_remove2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("Remove", type="secondary"):
                result = fetcher.remove_instrument(remove_symbol)
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
    else:
        st.info("No instruments tracked yet. Add some above!")

# ====================
# DASHBOARD PAGE
# ====================
elif page == "Dashboard":
    st.title("📊 ETF Analysis Dashboard")
    
    instruments = fetcher.get_all_instruments(active_only=True)
    
    if not instruments:
        st.warning("No instruments tracked. Go to 'Manage Instruments' to add some.")
    else:
        # Get latest prices
        symbols = [i['symbol'] for i in instruments]
        latest_prices = fetcher.get_latest_prices(symbols)
        
        # Display metrics in columns
        st.subheader("Portfolio Overview")
        
        cols = st.columns(min(4, len(instruments)))
        for idx, inst in enumerate(instruments[:4]):
            with cols[idx]:
                symbol = inst['symbol']
                if symbol in latest_prices:
                    price_info = latest_prices[symbol]
                    st.metric(
                        label=symbol,
                        value=f"${price_info['close']:.2f}",
                        delta=None
                    )
                    st.caption(inst['name'][:30])
        
        st.divider()
        
        # Quick refresh button
        st.subheader("Data Management")
        col_refresh1, col_refresh2 = st.columns([3, 1])
        
        with col_refresh1:
            refresh_symbol = st.selectbox(
                "Update price data for:",
                options=['All'] + symbols,
                key="refresh_select"
            )
        
        with col_refresh2:
            st.write("")
            st.write("")
            if st.button("Fetch Latest Data"):
                symbols_to_refresh = symbols if refresh_symbol == 'All' else [refresh_symbol]
                
                progress_bar = st.progress(0)
                for idx, sym in enumerate(symbols_to_refresh):
                    with st.spinner(f"Fetching {sym}..."):
                        result = fetcher.fetch_and_store_prices(sym, period='1mo')
                        if result['success']:
                            st.success(f"{sym}: {result['message']}")
                    progress_bar.progress((idx + 1) / len(symbols_to_refresh))
                
                st.rerun()
        
        st.divider()
        
        # Display instruments table with latest info
        st.subheader("All Tracked Instruments")
        
        display_data = []
        for inst in instruments:
            symbol = inst['symbol']
            row = {
                'Symbol': symbol,
                'Name': inst['name'],
                'Type': inst['type'],
                'Sector': inst['sector']
            }
            if symbol in latest_prices:
                row['Last Price'] = f"${latest_prices[symbol]['close']:.2f}"
                row['Last Update'] = latest_prices[symbol]['date'].strftime('%Y-%m-%d')
            else:
                row['Last Price'] = 'N/A'
                row['Last Update'] = 'N/A'
            
            display_data.append(row)
        
        st.dataframe(
            pd.DataFrame(display_data),
            use_container_width=True,
            hide_index=True
        )

# ====================
# PRICE HISTORY PAGE
# ====================
elif page == "Price History":
    st.title("📈 Price History")
    
    instruments = fetcher.get_all_instruments(active_only=True)
    
    if not instruments:
        st.warning("No instruments tracked. Go to 'Manage Instruments' to add some.")
    else:
        symbols = [i['symbol'] for i in instruments]
        
        # Selection controls
        col1, col2 = st.columns([2, 2])
        
        with col1:
            selected_symbol = st.selectbox("Select Instrument", options=symbols)
        
        with col2:
            period = st.selectbox(
                "Time Period",
                options=['1M', '3M', '6M', '1Y', '2Y', '5Y', 'All'],
                index=3
            )
        
        if selected_symbol:
            # Calculate date range
            end_date = datetime.now()
            if period == '1M':
                start_date = end_date - timedelta(days=30)
            elif period == '3M':
                start_date = end_date - timedelta(days=90)
            elif period == '6M':
                start_date = end_date - timedelta(days=180)
            elif period == '1Y':
                start_date = end_date - timedelta(days=365)
            elif period == '2Y':
                start_date = end_date - timedelta(days=730)
            elif period == '5Y':
                start_date = end_date - timedelta(days=1825)
            else:
                start_date = None
            
            # Get price data
            df = fetcher.get_price_data(selected_symbol, start_date=start_date, end_date=end_date)
            
            if not df.empty:
                # Calculate metrics
                latest_price = df['close'].iloc[-1]
                first_price = df['close'].iloc[0]
                price_change = latest_price - first_price
                pct_change = (price_change / first_price) * 100
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Current Price", f"${latest_price:.2f}")
                
                with col2:
                    st.metric("Change", f"${price_change:.2f}", f"{pct_change:+.2f}%")
                
                with col3:
                    st.metric("High", f"${df['high'].max():.2f}")
                
                with col4:
                    st.metric("Low", f"${df['low'].min():.2f}")
                
                # Price chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig.update_layout(
                    title=f"{selected_symbol} Price History",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    hovermode='x unified',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Volume chart
                fig_volume = go.Figure()
                
                fig_volume.add_trace(go.Bar(
                    x=df.index,
                    y=df['volume'],
                    name='Volume',
                    marker_color='lightblue'
                ))
                
                fig_volume.update_layout(
                    title=f"{selected_symbol} Trading Volume",
                    xaxis_title="Date",
                    yaxis_title="Volume",
                    height=300
                )
                
                st.plotly_chart(fig_volume, use_container_width=True)
                
                # Data table
                with st.expander("View Raw Data"):
                    st.dataframe(
                        df.reset_index().tail(50).sort_index(ascending=False),
                        use_container_width=True
                    )
            else:
                st.warning(f"No price data available for {selected_symbol}. Try fetching data from the Dashboard.")

# ====================
# COMPARATIVE ANALYSIS PAGE
# ====================
elif page == "Comparative Analysis":
    st.title("📊 Comparative Analysis")
    
    instruments = fetcher.get_all_instruments(active_only=True)
    
    if not instruments:
        st.warning("No instruments tracked. Go to 'Manage Instruments' to add some.")
    elif len(instruments) < 2:
        st.warning("Add at least 2 instruments to compare.")
    else:
        symbols = [i['symbol'] for i in instruments]
        
        # Multi-select for comparison
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_symbols = st.multiselect(
                "Select Instruments to Compare (max 5)",
                options=symbols,
                default=symbols[:min(3, len(symbols))],
                max_selections=5
            )
        
        with col2:
            period = st.selectbox(
                "Period",
                options=['1M', '3M', '6M', '1Y', 'All'],
                index=3
            )
        
        if len(selected_symbols) >= 2:
            # Calculate date range
            end_date = datetime.now()
            if period == '1M':
                start_date = end_date - timedelta(days=30)
            elif period == '3M':
                start_date = end_date - timedelta(days=90)
            elif period == '6M':
                start_date = end_date - timedelta(days=180)
            elif period == '1Y':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = None
            
            # Fetch data for all selected symbols
            all_data = {}
            for symbol in selected_symbols:
                df = fetcher.get_price_data(symbol, start_date=start_date, end_date=end_date)
                if not df.empty:
                    all_data[symbol] = df
            
            if all_data:
                # Normalize prices to percentage change
                st.subheader("Normalized Performance Comparison")
                
                fig = go.Figure()
                
                for symbol, df in all_data.items():
                    # Calculate percentage change from first value
                    normalized = ((df['close'] / df['close'].iloc[0]) - 1) * 100
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=normalized,
                        mode='lines',
                        name=symbol,
                        line=dict(width=2)
                    ))
                
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Return (%)",
                    hovermode='x unified',
                    height=500,
                    yaxis=dict(ticksuffix="%")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance metrics table
                st.subheader("Performance Metrics")
                
                metrics_data = []
                for symbol, df in all_data.items():
                    first_price = df['close'].iloc[0]
                    last_price = df['close'].iloc[-1]
                    pct_change = ((last_price / first_price) - 1) * 100
                    
                    metrics_data.append({
                        'Symbol': symbol,
                        'Start Price': f"${first_price:.2f}",
                        'End Price': f"${last_price:.2f}",
                        'Return': f"{pct_change:+.2f}%",
                        'High': f"${df['high'].max():.2f}",
                        'Low': f"${df['low'].min():.2f}",
                        'Avg Volume': f"{df['volume'].mean():,.0f}"
                    })
                
                st.dataframe(
                    pd.DataFrame(metrics_data),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No price data available for selected instruments. Fetch data from the Dashboard first.")
        else:
            st.info("Select at least 2 instruments to compare.")

# Footer
st.sidebar.divider()
st.sidebar.caption("ETF Analysis Dashboard")
st.sidebar.caption("Built with Streamlit")
